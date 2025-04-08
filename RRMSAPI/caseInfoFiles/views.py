from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CaseInfoDetailsSerializer,FileDetailsSerializer, CaseInfoSearchSerializers
from .models import FileDetails, CaseInfoDetails
from django.conf import settings
from django.db.models import Q
from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from mdm.permissions import HasRequiredPermission
from rest_framework.parsers import MultiPartParser, FormParser
import json
import hashlib
import os
import mimetypes

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads/")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create your views here.
class CaseInfoFilesSearchView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission]
    def post(self, request):
        searchParams = request.data
        query = Q()

        if "stateId" in searchParams:
            query |= Q(stateId__icontains= searchParams['stateId'])

        if "districtId" in searchParams:
            query |= Q(districtId__icontains= searchParams['districtId'])
        
        if "unitId" in searchParams:
            query |= Q(unitId__icontains= searchParams['unitId'])

        if "office" in searchParams:
            query |= Q(Office__icontains= searchParams['office'])

        if "caseNo" in searchParams:
            query |= Q(caseNo__icontains= searchParams['caseNo'])

        if "firNo" in searchParams:
            query |= Q(firNo__icontains= searchParams['firNo'])

        if "caseDate" in searchParams:
            query |= Q(caseDate__icontains= searchParams['caseDate'])

        caseDetails= CaseInfoDetails.objects.filter(query).prefetch_related('files')
        caseSerializer = CaseInfoSearchSerializers(caseDetails, many = True)
        return Response({"responseData":{"response":caseSerializer.data,"status":status.HTTP_200_OK}})
       
class CaseInfoDetailsView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission]
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        try:
            
            case_info_json = request.data.get("caseDetails")
            file_details = request.data.get("fileDetails")


            if not case_info_json:
                return Response({"responseData":{"error":"No Case Details","status":status.HTTP_400_BAD_REQUEST}})

            

            if isinstance(case_info_json, str):
                case_data= json.loads(case_info_json)

            if isinstance(file_details, str):
                file_details_data = json.loads(file_details)

                print('parsed file details json: ',file_details_data)

            case_serailizer = CaseInfoDetailsSerializer(data = case_data)

            if not case_serailizer.is_valid():
                return Response(case_serailizer.errors, status=status.HTTP_400_BAD_REQUEST)

            caseInfo = case_serailizer.save()

            uploaded_files = request.FILES.getlist("Files")

            if not uploaded_files:
                return Response({"error": "No files Uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            file_details_list = [] 

            for i in range(len(uploaded_files)):
                file_content = uploaded_files[i].read()

                # Compute file hash (SHA-256)
                file_hash = hashlib.sha256(file_content).hexdigest()
                
                # Define file path and save file
                file_name = uploaded_files[i].name
                file_path = os.path.join(UPLOAD_DIR, file_name)

                # Write file to disk
                with open(file_path, "wb") as f:
                    f.write(file_content)

                    print("file detail :",file_details_data[i])

                # Save file details in the database with casedetailsid
                file_detail = FileDetails.objects.create(
                    caseDetails=caseInfo,
                    fileName=file_name,
                    filePath=file_path,
                    fileHash=file_hash,
                    hashTag = file_details_data[i]['hashTag'],
                    subject = file_details_data[i]['subject'],
                    fileType = file_details_data[i]['fileType'],
                    classification = file_details_data[i]['classification']
                )

                file_details_list.append({
                    "file":FileDetailsSerializer(file_detail).data
                })
            return Response(
                {
                    "caseDetails": CaseInfoDetailsSerializer(caseInfo).data,
                    "file": file_details_list ,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class CaseInfoDetailsUpdateView(APIView):
#     def get_object(self,request):

class FilePreviewAPIView(APIView):
    def post(self,request):
        file_hash = request.data.get("fileHash")

        if not file_hash:
            return Response({"responseData":{"error": "fileHash is required", "status" : status.HTTP_400_BAD_REQUEST}})

        try:
            objFile = FileDetails.objects.get(fileHash = file_hash)
            filePath = objFile.filePath
            
            if not os.path.exists(filePath):
                raise FileNotFoundError("File not found on disk")

            mime_type, _ = mimetypes.guess_type(filePath)
            return FileResponse(open(filePath, 'rb'), content_type=mime_type or 'application/octet-stream')

        except FileDetails.DoesNotExist:
            raise Http404("No file with given hash")

        except FileNotFoundError:
            raise Http404("File path invalid or missing")
