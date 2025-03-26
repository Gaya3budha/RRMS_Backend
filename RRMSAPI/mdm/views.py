from django.shortcuts import render
from rest_framework import status
from .models import Role, DivisionMaster, DistrictMaster, StateMaster,UnitMaster, DesignationMaster
from .serializers import RoleSerializer, DivisionSerializer, DistrictSerializer, StateSerializer, DesignationSerializer, UnitSerializer
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
    def get(self,request,stateId, *args, **kwargs):
        # state_id = request.query_params.get('stateid', None)
        if stateId:
            districts = DistrictMaster.objects.filter(stateId=stateId).order_by('districtName')
        else:
            districts = DistrictMaster.objects.all()

        serializer = DistrictSerializer(districts, many= True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class DivisionListView(APIView):
    def get(self,request, *args, **kwargs):
        divisions = DivisionMaster.objects.all()
        serializer = DivisionSerializer(divisions, many= True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class DesignationListView(APIView):
    def get(self,request, *args, **kwargs):
        designations = DesignationMaster.objects.all()
        serializer = DesignationSerializer(designations, many= True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class UnitListView(APIView):
    def get(self,request, districtId, *args, **kwargs):
        if districtId:
            units = UnitMaster.objects.filter(districtId= districtId).order_by('unitName')
        else:
            units = UnitMaster.objects.all()

        serializer = UnitSerializer(units, many= True)
        return Response(serializer.data, status = status.HTTP_200_OK)