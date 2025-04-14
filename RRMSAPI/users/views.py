from django.shortcuts import render
from rest_framework import status,permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from .models import User
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
                return Response({"responseData": serializer_class.validated_data, "statusCode": 200}, status=status.HTTP_200_OK)
            return Response({"responseData":serializer_class.errors, "statusCode": 400}, status=status.HTTP_400_BAD_REQUEST)

        except AuthenticationFailed as e:
            return Response({"responseData":str(e), "statusCode": 401}, status=status.HTTP_401_UNAUTHORIZED)




