from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CaseInfoDetailsSerializer,FileDetailsSerializer
from .models import FileDetails
import json
import hashlib
from django.conf import settings
import os

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads/")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create your views here.
class CaseInfoFileUploadView(APIView):
    def post(self, request):
        try:
            
            case_info_json = request.data.get("caseDetails")

            if not case_info_json:
                return Response({"responseData":{"error":"No Case Details","status":status.HTTP_400_BAD_REQUEST}})

            case_data= json.loads(case_info_json)

            case_serailizer = CaseInfoDetailsSerializer(data = case_data)

            if not case_serailizer.is_valid():
                return Response(case_serailizer.errors, status=status.HTTP_400_BAD_REQUEST)

            caseInfo = case_serailizer.save()

            uploaded_files = request.FILES.getlist("Files")

            if not uploaded_files:
                return Response({"error": "No files Uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            file_details_list = [] 

            for uploaded_file in uploaded_files:
                file_content = uploaded_file.read()

                # Compute file hash (SHA-256)
                file_hash = hashlib.sha256(file_content).hexdigest()
                
                # Define file path and save file
                file_name = uploaded_file.name
                file_path = os.path.join(UPLOAD_DIR, file_name)

                # Write file to disk
                with open(file_path, "wb") as f:
                    f.write(file_content)

                # Save file details in the database with student_id
                file_detail = FileDetails.objects.create(
                    caseDetails=caseInfo,
                    fileName=file_name,
                    filePath=file_path,
                    fileHash=file_hash
                )

                file_details_list.append({
                    "file":FileDetailsSerializer(file_detail).data
                })
            return Response(
                {
                    "student": CaseInfoDetailsSerializer(caseInfo).data,
                    "file": file_details_list ,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)