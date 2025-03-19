from django.shortcuts import render
from rest_framework import status
from .models import Role, DivisionMaster, DistrictMaster, StateMaster
from .serializers import RoleSerializer, DivisionSerializer, DistrictSerializer, StateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class StateListView(APIView):
    def get(self,request,*args,**kwargs):
        roles = StateMaster.objects.all()
        serializer = StateSerializer(roles, many= True)
        return Response(serializer.data,status = status.HTTP_200_OK)

class RolesListView(APIView):
    def get(self,request,*args,**kwargs):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many= True)
        return Response(serializer.data,status = status.HTTP_200_OK)

class DistrictListView(APIView):
    def get(self,request, *args, **kwargs):
        state_id = request.query_params.get('stateid', None)

        if state_id:
            districts = DistrictMaster.objects.filter(stateId=state_id)
        else:
            districts = DistrictMaster.objects.all()

        serializer = DistrictSerializer(districts, many= True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class DivisionListView(APIView):
    def get(self,request, *args, **kwargs):
        divisions = DivisionMaster.objects.all()
        serializer = DivisionSerializer(divisions, many= True)
        return Response(serializer.data, status = status.HTTP_200_OK)