from .models import CaseInfoDetails, FileDetails
from rest_framework import serializers
import hashlib
import os
from mdm.models import StateMaster, DistrictMaster, UnitMaster
from cryptography.fernet import Fernet


class CaseInfoDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CaseInfoDetails
        fields = "__all__"

class FileDetailsSerializer(serializers.ModelSerializer):
    CaseInfoDetailsId = serializers.IntegerField(source='CaseInfoDetails.CaseInfoDetailsId',read_only = True)
    
    class Meta:
        model = FileDetails
        fields = ['fileId','CaseInfoDetailsId','fileName','filePath','fileHash']

class CaseInfoSearchSerializers(serializers.ModelSerializer):
    stateName = serializers.SerializerMethodField()
    districtName = serializers.SerializerMethodField()
    unitName = serializers.SerializerMethodField()


    files = FileDetailsSerializer(many= True, read_only= True)

    class Meta:
        model = CaseInfoDetails
        fields = ['CaseInfoDetailsId','stateId','stateName','districtId','districtName','unitId','unitName','Office','caseDate','caseNo','firNo','files']

    def get_stateName(self, obj):
        try:
            state = StateMaster.objects.get(stateId = obj.stateId)
            return state.stateName
        except StateMaster.DoesNotExist:
            return None

    def get_districtName(self, obj):
        try:
            dist = DistrictMaster.objects.get(districtId = obj.districtId)
            return dist.districtName
        except DistrictMaster.DoesNotExist:
            return None

    def get_unitName(self, obj):
        try:
            unit = UnitMaster.objects.get(unitId = obj.unitId)
            return unit.unitName
        except UnitMaster.DoesNotExist:
            return None
      