import logging
from rest_framework import serializers

from .models import  EmailDomain, Role,SMTPSettings,Department, DistrictMaster, Division, StateMaster, Designation,DesignationHierarchy, GeneralLookUp,UnitMaster, FileType, FileClassification, CaseStatus

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateMaster
        fields = ['stateId','stateName','active','lastModifiedDate']

class DepartmentSeriallizer(serializers.ModelSerializer):
    class Meta:
        model =Department
        fields = ['departmentId','departmentName']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['roleId','roleName']

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictMaster
        fields = ['districtId','districtName','localName','active','lastModifiedDate']

class DivisionSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(source='departmentId', read_only=True)
    departmentId = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = Division
        fields = ['divisionId', 'divisionName', 'departmentId', 'department']

class DesignationViewSerializer(serializers.ModelSerializer):
    division = DivisionSerializer(many=True,read_only=True)
    department = DepartmentSeriallizer(many=True,read_only=True)

    divisionIds = serializers.PrimaryKeyRelatedField(source='division',queryset=Division.objects.all(), many=True,required=False )
    departmentIds = serializers.PrimaryKeyRelatedField(source='department',queryset=Department.objects.all(), many=True,required=False )

    class Meta:
        model = Designation
        fields = ['designationId','designationName','division','department','divisionIds','departmentIds']

class DesignationSerializer(serializers.ModelSerializer):
    division = DivisionSerializer(many=True,read_only=True)
    # department = DepartmentSeriallizer(many=True,read_only=True)

    # divisionIds = serializers.PrimaryKeyRelatedField(source='division',queryset=Division.objects.all(), many=True)
    # departmentIds = serializers.PrimaryKeyRelatedField(source='department',queryset=Department.objects.all(), many=True)

    class Meta:
        model = Designation
        fields = ['designationId','designationName','division']

class DesignationHierarchySerializer(serializers.ModelSerializer):
    parent_designation_name = serializers.StringRelatedField(source='parent_designation', read_only=True)
    child_designation_name = serializers.StringRelatedField(source='child_designation', read_only=True)


    class Meta:
        model = DesignationHierarchy
        fields = [
            'id','parent_designation','parent_designation_name','child_designation','child_designation_name'
        ]

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitMaster
        fields = ['unitId','unitName','stateId','districtId','typeId','parentUnit','actualStrength',
        'sanctionedStrength','talukID','address1','address2','active','lastModifiedDate']

class FileTypeSerializer(serializers.ModelSerializer):
    fileTypeId = serializers.IntegerField(source='lookupId',read_only=True)
    fileTypeName = serializers.CharField(source='lookupName')
    class Meta:
        model = GeneralLookUp
        fields = ['fileTypeId','fileTypeName']

class SMTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTPSettings
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by', 'modified_at')

class EmailDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailDomain
        fields = '__all__'
        read_only_fields = ('domainId','created_by')

class DomainNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailDomain
        fields = ['domainName']

def get_serializer_class(self):
    if self.action == 'list':
        return DomainNameOnlySerializer
    return EmailDomainSerializer


class CaseFilesSerializer(serializers.ModelSerializer):
    caseFileId = serializers.IntegerField(source='lookupId',read_only=True)
    caseFileName = serializers.CharField(source='lookupName')
    class Meta:
        model = GeneralLookUp
        fields = ['caseFileId','caseFileName']

class CorrFilesSerializer(serializers.ModelSerializer):
    corrId = serializers.IntegerField(source='lookupId',read_only=True)
    corrFileName = serializers.CharField(source='lookupName')
    class Meta:
        model = GeneralLookUp
        fields = ['corrId','corrFileName']

class FileClassificationSerializer(serializers.ModelSerializer):
    fileClassificationId = serializers.IntegerField(source='lookupId',read_only=True)
    fileClassificationName = serializers.CharField(source='lookupName')
    class Meta:
        model = GeneralLookUp
        fields = ['fileClassificationId','fileClassificationName']

class CaseStatusSerializer(serializers.ModelSerializer):
    statusId = serializers.IntegerField(source='lookupId',read_only=True)
    statusName = serializers.CharField(source='lookupName')

    class Meta:
        model = GeneralLookUp
        fields = ['statusId','statusName']

class FinalReportCaseStatusSerializer(serializers.ModelSerializer):
    frstatusId = serializers.IntegerField(source='lookupId',read_only=True)
    frstatusName = serializers.CharField(source='lookupName')
    categoryId = serializers.IntegerField(source='CategoryId')

    class Meta:
        model = GeneralLookUp
        fields = ['frstatusId','frstatusName','categoryId']

class LookupCustomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='lookupid')
    value = serializers.CharField(source='lookupvalue')

    class Meta:
        model = GeneralLookUp
        fields = ['id', 'value']