import logging
from rest_framework import serializers

from .models import  Role,Department, DistrictMaster, Division, StateMaster, Designation, GeneralLookUp,UnitMaster, FileType, FileClassification, CaseStatus

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

class DesignationSerializer(serializers.ModelSerializer):
    division = DivisionSerializer(many=True,read_only=True)
    department = DepartmentSeriallizer(many=True,read_only=True)

    divisionIds = serializers.PrimaryKeyRelatedField(source='division',queryset=Division.objects.all(), many=True)
    departmentIds = serializers.PrimaryKeyRelatedField(source='department',queryset=Department.objects.all(), many=True)

    class Meta:
        model = Designation
        fields = ['designationId','designationName','division','divisionIds','departmentIds', 'department']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitMaster
        fields = ['unitId','unitName','stateId','districtId','typeId','parentUnit','actualStrength',
        'sanctionedStrength','talukID','address1','address2','active','lastModifiedDate']

# class FileTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FileType
#         fields = ['fileTypeId','fileTypeName','active','lastModifiedDate']

# class FileClassificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FileClassification
#         fields = ['fileClassificationId','fileClassificationName','active','lastModifiedDate']

# class CaseStatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CaseStatus
#         fields = ['statusId','statusName','active','lastModifiedDate']

class LookupCustomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='lookupid')
    value = serializers.CharField(source='lookupvalue')

    class Meta:
        model = GeneralLookUp
        fields = ['id', 'value']