from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, UserSearchSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import User, ActiveUser, Designation
# from rest_framework.permissions import IsAdminUser
from mdm.models import Role
from mdm.permissions import IsSuperAdminOrReadOnly
from datetime import date
from django.db.models import Q


# Create your views here.
class UserListView(APIView):
    def get(self,request,*args,**kwargs):
        user = request.user
        # division_id = request.query_params.get('division_id')

        # if not division_id:
        #     return Response({"detail": "divisionId is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.is_superuser:
            users=User.objects.all()
        # else:
        #     is_admin_of_division = UserDivisionRole.objects.filter(
        #         user=user,
        #         division__pk=division_id,
        #         role__roleName='Admin'  # or use role ID if preferred
        #     ).exists()

        #     if is_admin_of_division:
        #         users = User.objects.filter(
        #             userdivisionrole__division__pk = division_id
        #         ).distinct()
        #     else:
        #         return Response({"detail": "Not authorized for this division."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(users, many= True, context={'request': request})
        return Response(serializer.data,status = status.HTTP_200_OK)

class CreateUserView(APIView):
    permission_classes = [IsSuperAdminOrReadOnly]
    def post(self,request,*args,**kwargs):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data,status = status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class UserDivisionRoleCreateAPIView(APIView):
#    def post(self, request, *args, **kwargs):
#         data = request.data.copy()
        
#         user_id = data.get('user')
#         if not user_id:
#             return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = UserDivisionRoleCreateSerializer(data=data)
        
#         if serializer.is_valid():
#             serializer.save(user_id=user_id)  # pass user_id explicitly
#             return Response({"message": "Divsion added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UpdateUserView(APIView):
    def patch(self,request,kgid_user,*args,**kwargs):
        try:
            # getting the user based on kgid
            user = User.objects.get(kgid = kgid_user)

            # blank dictinary object
            updated_data = {}

            # updated_data['password']=request.data['password']
            # updated_data['set_password']=request.data['set_password']

            # checking if roleId is present in request body or not
            if 'roleId' in request.data:
                role_id = request.data['roleId']
                try:
                    new_role = Role.objects.get(roleId=role_id)
                    updated_data['role'] = new_role
                except Role.DoesNotExist:
                    return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

            # Handle designation update (many-to-many)
            if 'designationIds' in request.data:
                designation_ids = request.data['designationIds']
                if isinstance(designation_ids, list):
                    designations = Designation.objects.filter(id__in=designation_ids)
                    user.designation.set(designations)
                else:
                    return Response({"error": "designationIds must be a list"}, status=status.HTTP_400_BAD_REQUEST)

            # Apply any other updates (currently only role is handled via updated_data)
            for key, value in updated_data.items():
                setattr(user, key, value)

                user.save()

                serializer = UserSerializer(user,  context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "roleId field is required"}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        except Role.DoesNotExist:
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)


class CustomTokenObtainPairView(TokenObtainPairView):
    #  serializer_class = CustomTokenObtainPairSerializer
    def post(self,request):
        serializer_class = CustomTokenObtainPairSerializer(data = request.data)

        try:
            if serializer_class.is_valid():
                user = serializer_class.user
                ActiveUser.objects.update_or_create(user=user)
                return Response({"responseData": serializer_class.validated_data, "statusCode": 200}, status=status.HTTP_200_OK)
            return Response({"responseData":serializer_class.errors, "statusCode": 400}, status=status.HTTP_400_BAD_REQUEST)

        except AuthenticationFailed as e:
            return Response({"responseData":str(e), "statusCode": 401}, status=status.HTTP_401_UNAUTHORIZED)


class GetLoggedInUsersView(APIView):
    #  permission_classes = [IsAdminUser]
     
     def get(self, request, *args, **kwargs):
        active_users = ActiveUser.objects.select_related('user').filter(last_login__date=date.today())

        print('active_users',active_users)
        active_users_data = UserSerializer([a.user for a in active_users], many=True, context={'request': request})


        return Response({
            "count": active_users.count(),
            "users": active_users_data.data
        })

class GetDivisionrAdminsView(APIView):
    def post(self, request):
        divsion_id =request.data.get("division_id")
        role_id =request.data.get("role_id")

        print("role_id",role_id)
        print("division_id",divsion_id)

        users = User.objects.filter(role__roleId=3,designation__division__divisionId=divsion_id)

        print("users",users)
        serialized_users = UserSerializer(users, many=True)

        return Response({
            "users" : serialized_users.data
        })


class SearchUsersAPIView(APIView):
    def post(self, request):
        searchParams = request.data
        query = Q()
        filters_applied = False

        if "departmentId" in searchParams and searchParams["departmentId"] not in [None, ""]:
            query &= Q(designation__department__departmentId__icontains = searchParams['departmentId'])
            filters_applied = True

        if "divisionId" in searchParams and searchParams["divisionId"] not in [None, ""]:
            query &= Q(designation__division__divisionId__icontains= searchParams['divisionId'])
            filters_applied = True

        if "designationId" in searchParams and searchParams["designationId"] not in [None, ""]:
            query &= Q(designation__designationId__icontains= searchParams['designationId'])
            filters_applied = True
        
        if "firstName" in searchParams and searchParams["firstName"] not in [None, ""]:
            query &= Q(first_name__icontains= searchParams['firstName'])
            filters_applied = True

        if "lastName" in searchParams and searchParams["lastName"] not in [None, ""]:
            query &= Q(last_name__icontains= searchParams['lastName'])
            filters_applied = True

        if "mobileNo" in searchParams and searchParams["mobileNo"] not in [None, ""]:
            query &= Q(mobileno__icontains= searchParams['mobileNo'])
            filters_applied = True
        
        if "kgid" in searchParams and searchParams["kgid"] not in [None, ""]:
            query &= Q(kgid__icontains= searchParams['kgid'])
            filters_applied = True

        if filters_applied:
            queryset = User.objects.filter(query).prefetch_related('designation__division','designation__department').distinct()
        else:
            queryset = User.objects.none()

        serializer = UserSearchSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)