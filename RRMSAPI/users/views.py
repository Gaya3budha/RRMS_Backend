from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, RoleSerializer
from .models import User,Role

# Create your views here.
# @api_view(['POST'])
# def create_user(request):
#     if request.method == 'POST':
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save() 
#             return Response({
#                 'message': 'User created successfully',
#                 'user': UserSerializer(user).data
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RolesListView(APIView):
    def get(self,request,*args,**kwargs):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many= True)
        return Response(serializer.data,status = status.HTTP_200_OK)

class DistrictListView(APIView):
    def get(self,request, *args, **kwargs):
        districts = DistrictMaster.objects.all()
        serializer = DistrictSerializer(districts, many= True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class UserListView(APIView):
    def get(self,request,*args,**kwargs):
        users=User.objects.all()
        serializer = UserSerializer(users, many= True)
        return Response(serializer.data,status = status.HTTP_200_OK)

class CreateUserView(APIView):
    def post(self,request,*args,**kwargs):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save() 
            return Response(serializer.data,status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




