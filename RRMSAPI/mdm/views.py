from django.shortcuts import render
from rest_framework import status
from .models import Role, DivisionMaster, DistrictMaster, StateMaster,UnitMaster, DesignationMaster
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import HasRequiredPermission

# Create your views here.
class StateMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission]

    def get(self,request):
        states = StateMaster.objects.all().values("stateId","stateName")
        return Response({"responseData":list(states),"statusCode" :status.HTTP_200_OK})

class RoleView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission] 

    def get(self,request):
        roles = Role.objects.all().values("roleId","roleName")
        return Response({"responseData":list(roles),"statusCode" :status.HTTP_200_OK})

class DistrictMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission] 

    def get(self,request,stateId):
        if stateId:
            districts = DistrictMaster.objects.filter(stateId=stateId).order_by('districtName').values("districtId","districtName")
        else:
            districts = DistrictMaster.objects.all().values("districtId","districtName")

        return Response({"responseData":list(districts),"statusCode" :status.HTTP_200_OK})

class DivisionMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission] 

    def get(self,request):
        divisions = DivisionMaster.objects.all().values("divisionId","divisionName")
        return Response({"responseData":list(divisions),"statusCode" :status.HTTP_200_OK})

class DesignationMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission] 

    def get(self,request, *args, **kwargs):
        designations = DesignationMaster.objects.all().values("designationId","designationName")
        return Response({"responseData":list(designations),"statusCode" :status.HTTP_200_OK})

class UnitMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission] 

    def get(self,request, districtId, *args, **kwargs):
        if districtId:
            units = UnitMaster.objects.filter(districtId= districtId).order_by('unitName').values("unitId","unitName")
        else:
            units = UnitMaster.objects.all().values("unitId","unitName")

        return Response({"responseData":list(units),"statusCode" :status.HTTP_200_OK})