from django.shortcuts import render
from rest_framework import status,serializers
from .models import EmailDomain, Role,SMTPSettings,DesignationHierarchy, Department,Division,GeneralLookUp, DistrictMaster, StateMaster,UnitMaster, Designation, FileType, FileClassification, CaseStatus
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import HasRequiredPermission, IsSuperAdminOrReadOnly
from rest_framework import viewsets
from .serializers import DesignationHierarchySerializer,DesignationViewSerializer, EmailDomainSerializer, FinalReportCaseStatusSerializer,SMTPSerializer,CorrFilesSerializer,CaseFilesSerializer,FileTypeSerializer,FileClassificationSerializer,CaseStatusSerializer,DepartmentSeriallizer,LookupCustomSerializer, DivisionSerializer, DesignationSerializer
from rest_framework.permissions import IsAdminUser
from .utils import CATEGORY_LABELS
from rest_framework.generics import ListAPIView
from django.utils import timezone
from rest_framework.decorators import action

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
    permission_classes = [IsSuperAdminOrReadOnly]
    queryset = Designation.objects.all()
    serializer_class = DesignationViewSerializer

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

class SMTPViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdminOrReadOnly]
    queryset = SMTPSettings.objects.all()
    serializer_class = SMTPSerializer

    def get_queryset(self):
        queryset = SMTPSettings.objects.filter(isActive = True)
        print("count",queryset.count())
        return queryset
    
    def perform_create(self,serializer):
        serializer.save(
            created_by=self.request.user.id,
            modified_by=self.request.user.id,  # Optional: Track on creation
            modified_at=timezone.now()
        )
    
    def perform_update(self, serializer):
        serializer.save(
            modified_by=self.request.user.id,
            modified_at=timezone.now()
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.isActive = False
        instance.modified_by = request.user.id
        instance.modified_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdminOrReadOnly]
    queryset = EmailDomain.objects.all()
    serializer_class = EmailDomainSerializer

    def get_queryset(self):
        return EmailDomain.objects.all()

    def list(self, request, *args, **kwargs):
        active_qs = self.get_queryset().filter(isActive=True)
        serializer = self.get_serializer(active_qs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="names")
    def names(self, request):
        domains = (
            EmailDomain.objects
            .filter(isActive=True)
            .values_list("domainName", flat=True)
        )
        return Response(list(domains))
    
    def perform_create(self,serializer):
        serializer.save(
            created_by=self.request.user.id,
        )
    
    def perform_update(self, serializer):
        serializer.save(
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.isActive = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
  

class DesignationHierarchyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdminOrReadOnly]
    queryset = DesignationHierarchy.objects.all()
    serializer_class = DesignationHierarchySerializer

class UnitMasterView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission] 

    def get(self,request, districtId, *args, **kwargs):
        if districtId:
            units = UnitMaster.objects.filter(districtId= districtId).order_by('unitName').values("unitId","unitName")
        else:
            units = UnitMaster.objects.all().values("unitId","unitName")

        return Response({"responseData":list(units),"statusCode" :status.HTTP_200_OK})

class FileTypesViewSet(viewsets.ModelViewSet):
    serializer_class = FileTypeSerializer

    def get_queryset(self):
        return GeneralLookUp.objects.filter(active = 'Y',CategoryId=2).order_by("lookupId")

    def perform_create(self, serializer):
        serializer.save(CategoryId=2, active='Y')

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CaseFilesViewSet(viewsets.ModelViewSet):
    serializer_class = CaseFilesSerializer

    def get_queryset(self):
        return GeneralLookUp.objects.filter(active = 'Y',CategoryId=3).order_by("lookupId")

    def perform_create(self, serializer):
        serializer.save(CategoryId=3, active='Y')

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CorrespondenceFilesViewSet(viewsets.ModelViewSet):
    serializer_class = CorrFilesSerializer

    def get_queryset(self):
        return GeneralLookUp.objects.filter(active = 'Y',CategoryId=4).order_by("lookupId")

    def perform_create(self, serializer):
        serializer.save(CategoryId=4, active='Y')

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FileClassificationViewSet(viewsets.ModelViewSet):
    serializer_class = FileClassificationSerializer

    def get_queryset(self):
        return GeneralLookUp.objects.filter(active = 'Y',CategoryId=7).order_by("lookupId")

    def perform_create(self, serializer):
        serializer.save(CategoryId=7, active='Y')

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CaseStatusViewSet(viewsets.ModelViewSet):
    serializer_class = CaseStatusSerializer

    def get_queryset(self):
        return GeneralLookUp.objects.filter(active = 'Y',CategoryId=6).order_by("lookupId")

    def perform_create(self, serializer):
        serializer.save(CategoryId=6, active='Y')

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class FinalReportCaseStatusViewSet(viewsets.ModelViewSet):
    serializer_class = FinalReportCaseStatusSerializer

    def get_queryset(self):
        category_id = self.request.query_params.get('categoryId')
        queryset = GeneralLookUp.objects.filter(active='Y')
        if category_id:
            queryset = queryset.filter(CategoryId=category_id)
        return queryset.order_by('lookupId')

    def perform_create(self, serializer):
        category_id = self.request.data.get('categoryId')
        if not category_id:
            raise serializers.ValidationError({"categoryId": "This field is required."})
        serializer.save(CategoryId=category_id, active='Y')

    def perform_update(self, serializer):
        category_id = self.request.data.get('categoryId')
        if not category_id:
            raise serializers.ValidationError({"categoryId": "This field is required."})
        serializer.save(CategoryId=category_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = 'N'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

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

    

    