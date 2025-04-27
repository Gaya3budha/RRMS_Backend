from django.shortcuts import render
from rest_framework import status,permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, UserDivisionRoleCreateSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import User, ActiveUser, UserDivisionRole
from rest_framework.permissions import IsAdminUser
from mdm.models import Role


# Create your views here.
class UserListView(APIView):
    def get(self,request,*args,**kwargs):
        users=User.objects.all()
        serializer = UserSerializer(users, many= True, context={'request': request})
        return Response(serializer.data,status = status.HTTP_200_OK)

class CreateUserView(APIView):
    def post(self,request,*args,**kwargs):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data,status = status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserDivisionRoleCreateAPIView(APIView):
   def post(self, request, *args, **kwargs):
        data = request.data.copy()
        
        user_id = data.get('user')
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserDivisionRoleCreateSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(user_id=user_id)  # pass user_id explicitly
            return Response({"message": "Divsion added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UpdateUserView(APIView):
    def patch(self,request,kgid_user,*args,**kwargs):
        try:
            # getting the user based on kgid
            user = User.objects.get(kgid = kgid_user)

            # blank dictinary object
            updated_data = {}

            # checking if roleId is present in request body or not
            if 'roleId' in request.data:
                role_id = request.data['roleId']

                # fetching the passed roleId in role table
                new_role = Role.objects.get(roleId=role_id)

                # assigning to dict object
                updated_data['role']= new_role

                
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
     permission_classes = [IsAdminUser]
     
     def get(self, request, *args, **kwargs):
        active_users = ActiveUser.objects.select_related('user').all()
        active_users_data = UserSerializer([a.user for a in active_users], many=True, context={'request': request})


        return Response({
            "count": active_users.count(),
            "users": active_users_data.data
        })

class GetDivisionrAdminsView(APIView):
    def post(self, request):
        current_user =request.data.get("division_id")
        role_id =request.data.get("role_id")

        print("role_id",role_id)
        print("division_id",current_user)
        # given_role_users = User.objects.filter(role_id = role_id, divisionmaster_id = current_user)
        given_role_users= UserDivisionRole.objects.filter(role=role_id, division= current_user)

        user_ids = given_role_users.values_list('user_id', flat=True)
        users = User.objects.filter(id__in=user_ids)

        print("given role users of a division:",given_role_users)
        print("users",users)
        serialized_users = UserSerializer(users, many=True)

        return Response({
            "users" : serialized_users.data
        })


