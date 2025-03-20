from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User

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




