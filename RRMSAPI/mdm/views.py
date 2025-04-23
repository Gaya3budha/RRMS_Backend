from django.shortcuts import render
from rest_framework import status
from .models import Role, DivisionMaster, DistrictMaster, StateMaster,UnitMaster, DesignationMaster, FileType, FileClassification, CaseStatus
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import HasRequiredPermission
from rest_framework import viewsets
from .serializers import RoleSerializer, DivisionSerializer, DesignationSerializer, FileClassificationSerializer, FileTypeSerializer, CaseStatusSerializer
from rest_framework.permissions import IsAdminUser

# Create your views here.
class StateMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission]

    def get(self,request):
        states = StateMaster.objects.all().values("stateId","stateName")
        return Response({"responseData":list(states),"statusCode" :status.HTTP_200_OK})

# class RoleViewSet(viewsets.ModelViewSet):
#     queryset = Role.objects.all()
#     serializer_class = RoleSerializer
#     permission_classes = [IsAdminUser]

class DistrictMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission] 

    def get(self,request,stateId):
        if stateId:
            districts = DistrictMaster.objects.filter(stateId=stateId).order_by('districtName').values("districtId","districtName")
        else:
            districts = DistrictMaster.objects.all().values("districtId","districtName")

        return Response({"responseData":list(districts),"statusCode" :status.HTTP_200_OK})

class DivisionViewSet(viewsets.ModelViewSet):
    # queryset = DivisionMaster.objects.all()
    serializer_class = DivisionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return DivisionMaster.objects.filter(active = 'Y')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DesignationViewSet(viewsets.ModelViewSet):
    # queryset = DesignationMaster.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsAdminUser]
    def get_queryset(self):
        return DesignationMaster.objects.filter(active = 'Y')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UnitMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission] 

    def get(self,request, districtId, *args, **kwargs):
        if districtId:
            units = UnitMaster.objects.filter(districtId= districtId).order_by('unitName').values("unitId","unitName")
        else:
            units = UnitMaster.objects.all().values("unitId","unitName")

        return Response({"responseData":list(units),"statusCode" :status.HTTP_200_OK})

class FileTypesViewSet(viewsets.ModelViewSet):
    # queryset = FileType.objects.all()
    serializer_class = FileTypeSerializer

    def get_queryset(self):
        return FileType.objects.filter(active = 'Y')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FileClassificationViewSet(viewsets.ModelViewSet):
    # queryset = FileClassification.objects.all()
    serializer_class = FileClassificationSerializer

    def get_queryset(self):
        return FileClassification.objects.filter(active = 'Y')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CaseStatusViewSet(viewsets.ModelViewSet):
    # queryset = CaseStatus.objects.all()
    serializer_class = CaseStatusSerializer

    def get_queryset(self):
        return CaseStatus.objects.filter(active = 'Y')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    

    