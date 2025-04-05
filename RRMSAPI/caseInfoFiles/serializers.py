from .models import CaseInfoDetails, FileDetails
from rest_framework import serializers
import hashlib
import os
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
    files = FileDetailsSerializer(many= True, read_only= True)

    class Meta:
        model = CaseInfoDetails
        fields = ['stateId','districtId','unitId','Office','caseDate','caseNo','firNo','files']

# class FileUploadSerializer(serializers.Serializer):

#     caseDetails =CaseInfoDetailsSerializer()
#     file = serializers.FileField()

#     def create(self, validated_data):

#         caseData = validated_data.get("caseDetails")
#         file = validated_data.get("file")

#         # case_serializer = CaseInfoDetailsSerializer(data = caseData)

#         caseDetails = CaseInfoDetails.objects.create(
#             stateId = caseData['stateId'],
#             districtId = caseData['districtId'],
#             unitId = caseData['unitId'],
#             year = caseData['year'],
#             caseNo = caseData['caseNo'],
#             registeredDate = caseData['registeredDate'],
#             status = caseData['status'],
#             location = caseData['location'],
#             actSection = caseData['actSection'],
#         )
        
#         filePath, fileHash = self.save_file(file)

#         file_details = FileDetails.objects.create(
#             caseDetails=caseDetails,  # ForeignKey to User model
#             fileName=file.name,
#             filePath=filePath,
#             fileHash=fileHash
#         )

#         return file_details

#         def save_file(self, file):
#             # Encryption key (make sure to securely store and not hardcode it in production)
#             ENCRYPTION_KEY = b'54345-ABCRD-456'
#             cipher_suite = Fernet(ENCRYPTION_KEY)

#             # Folder to store uploaded files
#             UPLOAD_FOLDER = 'uploads/'

#             # Ensure the folder exists
#             if not os.path.exists(UPLOAD_FOLDER):
#                 os.makedirs(UPLOAD_FOLDER)

#             # Save the file
#             file_path = os.path.join(UPLOAD_FOLDER, file.name)
#             with open(file_path, 'wb+') as destination:
#                 for chunk in file.chunks():
#                     destination.write(chunk)

#             # Calculate file hash (SHA-256)
#             file_hash = hashlib.sha256()
#             with open(file_path, 'rb') as f:
#                 while chunk := f.read(4096):
#                     file_hash.update(chunk)
#             file_hash_hex = file_hash.hexdigest()

#             # Encrypt file path
#             encrypted_file_path = cipher_suite.encrypt(file_path.encode('utf-8')).decode('utf-8')

#             return encrypted_file_path, file_hash_hex

      