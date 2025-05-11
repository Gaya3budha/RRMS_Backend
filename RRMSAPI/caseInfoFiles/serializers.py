from .models import CaseInfoDetails, FileDetails, FavouriteFiles, Notification, FileAccessRequest,FileUploadApproval
from rest_framework import serializers
import hashlib
import os
from mdm.models import StateMaster, DistrictMaster, UnitMaster
from cryptography.fernet import Fernet

class FileUploadApprovalSerializer(serializers.ModelSerializer):
    division_name = serializers.CharField(source='division.divisionName', read_only=True)
    requested_by_first_name = serializers.CharField(source='requested_by.first_name', read_only=True)
    requested_by_last_name = serializers.CharField(source='requested_by.last_name', read_only=True)
    reviewed_by_first_name = serializers.CharField(source='reviewed_by.first_name', read_only=True)
    reviewed_by_last_name = serializers.CharField(source='reviewed_by.last_name', read_only=True)
    file_name = serializers.CharField(source='file.fileName', read_only=True)
    case_no = serializers.CharField(source='case_details_id.caseNo', read_only=True)

    class Meta:
        model = FileUploadApproval
        fields = [
            'id','status','file','file_name','case_details_id','case_no','requested_by','requested_by_first_name',
            'requested_by_last_name','reviewed_by','reviewed_by_first_name','reviewed_by_last_name','reviewed_at',
            'department','division','division_name','is_approved','comments','created_at'
        ]

class CaseInfoDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CaseInfoDetails
        fields = "__all__"
    
    def validate_caseNo(self,value):
        if CaseInfoDetails.objects.filter(caseNo=value).exists():
            raise serializers.ValidationError("(CCMS)Case No/ Enquiry No already exists")
        
        return value

class FileDetailsSearchSerializer(serializers.ModelSerializer):
    CaseInfoDetailsId = serializers.IntegerField(source='CaseInfoDetails.CaseInfoDetailsId',read_only = True)
    is_favourited = serializers.BooleanField(read_only=True)
    is_access_request_approved = serializers.BooleanField()
    classification_name = serializers.CharField(source='classification.fileClassificationName', read_only=True)
    is_request_raised = serializers.BooleanField()
    filetype_name = serializers.CharField(source='fileType.fileTypeName', read_only=True)

    class Meta:
        model = FileDetails
        fields = ['fileId','CaseInfoDetailsId','fileName','filePath','fileHash','hashTag','subject','fileType','filetype_name','classification','classification_name','uploaded_by','is_approved','is_favourited','is_access_request_approved','is_request_raised','documentType','comments']

class FileDetailsSerializer(serializers.ModelSerializer):
    CaseInfoDetailsId = serializers.IntegerField(source='CaseInfoDetails.CaseInfoDetailsId',read_only = True)
    is_favourited = serializers.BooleanField(read_only=True)
    classification_name = serializers.CharField(source='classification.fileClassificationName', read_only=True)
    filetype_name = serializers.CharField(source='fileType.fileTypeName', read_only=True)

    class Meta:
        model = FileDetails
        fields = ['fileId','CaseInfoDetailsId','fileName','filePath','fileHash','hashTag','subject','fileType','classification','uploaded_by','documentType','classification_name','is_favourited', 'filetype_name']  
        # 'classification_name','is_favourited', 'filetype_name'

class CaseInfoSearchSerializers(serializers.ModelSerializer):
    stateName = serializers.SerializerMethodField()
    districtName = serializers.SerializerMethodField()
    unitName = serializers.SerializerMethodField()
    caseDate = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")


    files = FileDetailsSearchSerializer(many= True, read_only= True)

    class Meta:
        model = CaseInfoDetails
        fields = ['CaseInfoDetailsId','stateId','stateName','districtId','districtName','unitId','unitName','Office','caseDate','caseNo','firNo','letterNo','caseType','author','toAddr','files']

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

class FavouriteSerializer(serializers.ModelSerializer):
    file = FileDetailsSerializer(read_only = True)

    class Meta:
        model = FavouriteFiles
        fields = ['id','file','added_at']


class NotificationSerializer(serializers.ModelSerializer):
    file = FileDetailsSerializer()
    
    class Meta:
        model = Notification
        fields = "__all__"

class FileAccessRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.firtsName', read_only=True)
    requested_to_name = serializers.CharField(source='requested_to.firstName', read_only=True)
    file_name = serializers.CharField(source='file.fileName', read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")

    class Meta:
        model = FileAccessRequest
        fields = [
            'id',
            'file_name',
            'requested_by_name',
            'requested_to_name',
            'is_approved',
            'comments',
            'created_at',
            'status'
        ]