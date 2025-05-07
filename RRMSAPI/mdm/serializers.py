import logging
from rest_framework import serializers

from .models import  Role, DistrictMaster, DivisionMaster, StateMaster, DesignationMaster, GeneralLookUp,UnitMaster, FileType, FileClassification, CaseStatus

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateMaster
        fields = ['stateId','stateName','active','lastModifiedDate']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['roleId','roleName']

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictMaster
        fields = ['districtId','districtName','localName','active','lastModifiedDate']

class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DivisionMaster
        fields = ['divisionId','divisionName','active','lastModifiedDate']

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignationMaster
        fields = ['designationId','designationName','active','lastModifiedDate']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitMaster
        fields = ['unitId','unitName','stateId','districtId','typeId','parentUnit','actualStrength',
        'sanctionedStrength','talukID','address1','address2','active','lastModifiedDate']

class FileTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileType
        fields = ['fileTypeId','fileTypeName','active','lastModifiedDate']

class FileClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileClassification
        fields = ['fileClassificationId','fileClassificationName','active','lastModifiedDate']

class CaseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseStatus
        fields = ['statusId','statusName','active','lastModifiedDate']

class LookupCustomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='lookupid')
    value = serializers.CharField(source='lookupvalue')

    class Meta:
        model = GeneralLookUp
        fields = ['id', 'value']