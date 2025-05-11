from django.shortcuts import render
from rest_framework import status
from .models import Role, Department,Division,GeneralLookUp, DistrictMaster, StateMaster,UnitMaster, Designation, FileType, FileClassification, CaseStatus
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import HasRequiredPermission, IsSuperAdminOrReadOnly
from rest_framework import viewsets
from .serializers import RoleSerializer,DepartmentSeriallizer,LookupCustomSerializer, DivisionSerializer, DesignationSerializer
from rest_framework.permissions import IsAdminUser
from .utils import CATEGORY_LABELS
from rest_framework.generics import ListAPIView

# Create your views here.
class StateMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission]

    def get(self,request):
        states = StateMaster.objects.all().values("stateId","stateName")
        return Response({"responseData":list(states),"statusCode" :status.HTTP_200_OK})
    
class DepartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdminOrReadOnly]
    queryset = Department.objects.all()
    serializer_class = DepartmentSeriallizer

    def get_queryset(self):
        return Department.objects.filter(active='Y')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class RoleViewSet(viewsets.ModelViewSet):
#     queryset = Role.objects.all()
#     serializer_class = RoleSerializer
#     permission_classes = [IsAdminUser]

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

class DivisionViewSet(viewsets.ModelViewSet):
    # # queryset = DivisionMaster.objects.all()
    # serializer_class = DivisionSerializer
    # # permission_classes = [HasRequiredPermission]

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_staff:  # admin user
    #             return DivisionMaster.objects.filter(active='Y')
    #     else:
    #             division_id = self.request.query_params.get('division_id')
    #             if division_id:
    #                 return DivisionMaster.objects.filter(divisionId=division_id, active='Y')
    #             else:
    #                 return DivisionMaster.objects.none()
    #     # return DivisionMaster.objects.none()

    # def get_permissions(self):
    #     if self.request.user and self.request.user.is_staff:
    #         permission_classes = [IsAdminUser]
    #     else:
    #         permission_classes = [HasRequiredPermission]
    #     return [permission() for permission in permission_classes]
    
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     instance.active = 'N'
    #     instance.save()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    permission_classes = [IsSuperAdminOrReadOnly]
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer

    def get_queryset(self):
        queryset = Division.objects.filter(active='Y')
        department_id = self.request.query_params.get('departmentId')

        if department_id:
            queryset = queryset.filter(departmentId=department_id,active='Y')
        return queryset


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DesignationViewSet(viewsets.ModelViewSet):
    # # queryset = DesignationMaster.objects.all()
    # serializer_class = DesignationSerializer
    # # permission_classes = [IsAdminUser]
    # def get_queryset(self):
    #     return DesignationMaster.objects.filter(active = 'Y')

    # def get_permissions(self):
    #     if self.request.user and self.request.user.is_staff:
    #         permission_classes = [IsAdminUser]
    #     else:
    #         permission_classes = [HasRequiredPermission]
    #     return [permission() for permission in permission_classes]
    
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     instance.active = 'N'
    #     instance.save()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    permission_classes = [IsSuperAdminOrReadOnly]
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

    def get_queryset(self):
        queryset = Designation.objects.filter(active='Y')
        print("count",queryset.count())
        department_id = self.request.query_params.get('departmentId')
        division_id = self.request.query_params.get('divisionId')

        print("department id",department_id)
        if department_id:
            queryset = queryset.filter(department__departmentId=department_id)
            print("department flltered records",queryset)

        if division_id:
            queryset = queryset.filter(division__divisionId=division_id)

        return queryset

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

# class FileTypesViewSet(viewsets.ModelViewSet):
#     # queryset = FileType.objects.all()
#     serializer_class = FileTypeSerializer

#     def get_queryset(self):
#         return FileType.objects.filter(active = 'Y')

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.active = 'N'
#         instance.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class FileClassificationViewSet(viewsets.ModelViewSet):
#     # queryset = FileClassification.objects.all()
#     serializer_class = FileClassificationSerializer

#     def get_queryset(self):
#         return FileClassification.objects.filter(active = 'Y').values('fileClassificationId','fileClassificationName','active')

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.active = 'N'
#         instance.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class CaseStatusViewSet(viewsets.ModelViewSet):
#     # queryset = CaseStatus.objects.all()
#     serializer_class = CaseStatusSerializer

#     def get_queryset(self):
#         return CaseStatus.objects.filter(active = 'Y').values('statusId','statusName','active')

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.active = 'N'
#         instance.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    

class LookupByCategoryView(ListAPIView):
    serializer_class = LookupCustomSerializer

    def get_queryset(self):
        return GeneralLookUp.objects.filter(active='Y').order_by('CategoryId','lookupOrder')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        grouped = {}
        for lookup in queryset:
            category_id = lookup.CategoryId
            label = CATEGORY_LABELS.get(category_id, f"Category_{category_id}")
            item = {
                "id": lookup.lookupId,
                "value": lookup.lookupName
            }
            grouped.setdefault(label, []).append(item)

        return Response(grouped)

    

    