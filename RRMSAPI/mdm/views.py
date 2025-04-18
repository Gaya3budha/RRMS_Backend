from django.shortcuts import render
from rest_framework import status
from .models import Role, DivisionMaster, DistrictMaster, StateMaster,UnitMaster, DesignationMaster
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import HasRequiredPermission
from rest_framework import viewsets
from .serializers import RoleSerializer, DivisionSerializer, DesignationSerializer
from rest_framework.permissions import IsAdminUser

# Create your views here.
class StateMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission]

    def get(self,request):
        states = StateMaster.objects.all().values("stateId","stateName")
        return Response({"responseData":list(states),"statusCode" :status.HTTP_200_OK})

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]

class DistrictMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission] 

    def get(self,request,stateId):
        if stateId:
            districts = DistrictMaster.objects.filter(stateId=stateId).order_by('districtName').values("districtId","districtName")
        else:
            districts = DistrictMaster.objects.all().values("districtId","districtName")

        return Response({"responseData":list(districts),"statusCode" :status.HTTP_200_OK})

class DivisionViewSet(viewsets.ModelViewSet):
    queryset = DivisionMaster.objects.all()
    serializer_class = DivisionSerializer
    permission_classes = [IsAdminUser]

class DesignationViewSet(viewsets.ModelViewSet):
    queryset = DesignationMaster.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsAdminUser]

class UnitMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission] 

    def get(self,request, districtId, *args, **kwargs):
        if districtId:
            units = UnitMaster.objects.filter(districtId= districtId).order_by('unitName').values("unitId","unitName")
        else:
            units = UnitMaster.objects.all().values("unitId","unitName")

        return Response({"responseData":list(units),"statusCode" :status.HTTP_200_OK})