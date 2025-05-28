from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CaseInfoDetailsSerializer,FileDetailsUpdateSerializer,FavouriteFileDetailsSerializer,FileUploadApprovalSerializer,FileAccessRequestSerializer,FileDetailsSerializer,NotificationSerializer, CaseInfoSearchSerializers, FavouriteSerializer
from .models import FileDetails, CaseInfoDetails, FavouriteFiles, Notification, FileAccessRequest, FileUploadApproval
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, OuterRef, Exists, Case, When, Value, BooleanField
from .utils import record_file_access, timezone
from django.conf import settings
from django.db.models import Q
from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from mdm.permissions import HasRequiredPermission
from mdm.models import FileClassification, GeneralLookUp, Division, Designation
# from users.models import UserDivisionRole
from rest_framework.parsers import MultiPartParser, FormParser
from .permissions import HasCustomPermission,FileDetailsPermission
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
import json
import hashlib
import os
import mimetypes
import traceback
from datetime import timedelta
import pandas as pd
from docx2pdf import convert
import base64

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads","CID")
os.makedirs(UPLOAD_DIR, exist_ok=True)

User = get_user_model()

# Create your views here.
class LatestUserFilesView(ListAPIView):
    serializer_class = FavouriteFileDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        three_days_ago = timezone.now() - timedelta(days=3)
        return FileDetails.objects.filter(uploaded_by=self.request.user,created_at__gte=three_days_ago).order_by('-created_at')[:20]  # Adjust limit as needed


class FavouriteFilesView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission]

    def get(self,request):
        division_id = request.query_params.get("division_id")
        favs= FavouriteFiles.objects.filter(user=request.user,division_id=division_id).order_by('-added_at')
        serializer = FavouriteSerializer(favs, many=True)
        return Response(serializer.data)

    def post(self, request, file_id):
        division_id = request.query_params.get("division_id")
        division = Division.objects.get(divisionId = division_id)
        try:
            file = FileDetails.objects.get(fileId=file_id)
            fav, created = FavouriteFiles.objects.get_or_create(user=request.user, file=file, division = division)
            if not created:
                record_file_access(request.user, file)
                return Response({'message': 'Already in favorites'}, status=status.HTTP_200_OK)
            return Response({'is_favourited':True, 'message': 'Added to favorites'}, status=status.HTTP_201_CREATED)
        except FileDetails.DoesNotExist:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,file_id):
        try:
            fav = FavouriteFiles.objects.get(user = request.user,file_id = file_id)
            file = FileDetails.objects.get(fileId = file_id)
            fav.delete()
            record_file_access(request.user, file)

            return Response({'is_favourited':False,'message':'Removed from favourites'},status= status.HTTP_200_OK)
        except FavouriteFiles.DoesNotExist:
            return Response({'error': 'This file is not favourited'}, status=status.HTTP_404_NOT_FOUND)
  

class SearchCaseFilesView(APIView):
    permission_classes = [HasCustomPermission]
    required_permission = 'view_caseinfodetails'

    def post(self, request):
        searchParams = request.data
        query = Q()
        filters_applied = False

        if "division_id" in searchParams:
            query &= Q(division__divisionId__icontains= searchParams['division_id'])
            filters_applied = True

        if "stateId" in searchParams:
            query &= Q(stateId__icontains= searchParams['stateId'])
            filters_applied = True

        if "districtId" in searchParams and searchParams["districtId"] not in [None, ""]:
            query &= Q(districtId__icontains= searchParams['districtId'])
            filters_applied = True
        
        if "unitId" in searchParams and searchParams["unitId"] not in [None, ""]:
            query &= Q(unitId__icontains= searchParams['unitId'])
            filters_applied = True

        if "office" in searchParams and searchParams["office"] not in [None, ""]:
            query &= Q(Office__icontains= searchParams['office'])
            filters_applied = True

        if "letterNo" in searchParams and searchParams["letterNo"] not in [None, ""]:
            query &= Q(letterNo__icontains= searchParams['letterNo'])
            filters_applied = True

        if "caseNo" in searchParams and searchParams["caseNo"] not in [None, ""]:
            query &= Q(caseNo__icontains= searchParams['caseNo'])
            filters_applied = True

        if "firNo" in searchParams and searchParams["firNo"] not in [None, ""]:
            query &= Q(firNo__icontains= searchParams['firNo'])
            filters_applied = True

        if "caseDate" in searchParams and searchParams["caseDate"] not in [None, ""]:
            query &= Q(caseDate__icontains= searchParams['caseDate'])
            filters_applied = True
        
        if "caseType" in searchParams and searchParams["caseType"] not in [None, ""]:
            query &= Q(caseType__icontains= searchParams['caseType'])
            filters_applied = True
        
        if "caseStatus" in searchParams and searchParams["caseStatus"] not in [None, ""]:
            query &= Q(caseStatus__icontains= searchParams['caseStatus'])
            filters_applied = True

        if "author" in searchParams and searchParams["author"] not in [None, ""]:
            query &= Q(author__icontains= searchParams['author'])
            filters_applied = True

        if "toAddr" in searchParams and searchParams["toAddr"] not in [None, ""]:
            query &= Q(toAddr__icontains= searchParams['toAddr'])
            filters_applied = True
        
        if "fromYear" in searchParams and searchParams["fromYear"] not in [None, ""]:
            query &= Q(year__gte= searchParams['fromYear'])
            filters_applied = True

        if "toYear" in searchParams and searchParams["toYear"] not in [None, ""]:
            query &= Q(year__lte= searchParams['toYear'])
            filters_applied = True

        query &= Q(is_draft__icontains = False)
        
        if filters_applied:
            case_details_qs = CaseInfoDetails.objects.filter(query).distinct()
        else:
            case_details_qs = CaseInfoDetails.objects.all()

        user = request.user


        request_raised_subquery = FileAccessRequest.objects.filter(
                    file=OuterRef('pk'),
                    requested_by=user
                    )
        access_request_subquery = FileAccessRequest.objects.filter(
                    file=OuterRef('pk'),
                    requested_by=user,
                    is_approved=True 
                    )
        favourite_subquery = FavouriteFiles.objects.filter(user=request.user,file=OuterRef('pk'))
        
        print('user.role.roleId',user.role.roleId)
        if user.is_staff or user.role.roleId in [3]:
            file_filter = Q()  # content manager sees all
        else:
           
            file_filter = Q(is_approved=True) | Q(uploaded_by=user) | Exists(access_request_subquery)

        file_extra_filter = Q()

        if 'hashtag' in searchParams and searchParams["hashtag"] not in [None, ""]:
            file_extra_filter &= Q(files__hashTag__icontains=searchParams['hashtag'])
            filters_applied = True

        if 'subject' in searchParams and searchParams["subject"] not in [None, ""]:
            file_extra_filter &= Q(files__subject__icontains= searchParams['subject'])
            filters_applied = True

        if 'classification' in searchParams and searchParams["classification"] not in [None, ""]:
            file_extra_filter &= Q(files__classification__lookupId__icontains= searchParams['classification'])
            filters_applied = True

        if 'fileType' in searchParams and searchParams["fileType"] not in [None, ""]:
            file_extra_filter &= Q(files__fileType__lookupId__icontains= searchParams['fileType'])
            filters_applied = True

        if 'docType' in searchParams and searchParams["docType"] not in [None, ""]:
            file_extra_filter &= Q(files__documentType__lookupId__icontains= searchParams['docType'])
            filters_applied = True

        if 'fileExt' in searchParams and searchParams["fileExt"]:
            file_ext = searchParams['fileExt']
            extensions = []

            if file_ext.lower() == 'image':
                extensions = ['.jpg', '.jpeg', '.png']
            elif file_ext.lower() == 'document':
                extensions = ['.pdf', '.docx', '.xlsx']
            elif file_ext.lower() == 'audio':
                extensions = ['.MP3','.mp3', '.WAV', '.FLAC']
            elif file_ext.lower() == 'video':
                extensions = ['.MP4','.mp4', '.MOV', '.mov','.WebM','.webm']

            if extensions:
                ext_query = Q()
                for ext in extensions:
                    ext_query |= Q(fileName__iendswith=ext)
                file_extra_filter &= ext_query


        file_queryset = FileDetails.objects.select_related('classification').filter(file_filter & file_extra_filter).annotate(
            is_favourited=Exists(favourite_subquery),
            is_request_raised = Exists(request_raised_subquery),
            is_access_request_approved=Exists(access_request_subquery)
            )

        print('file_extra_filter:',file_queryset.count())

        caseDetails = case_details_qs.prefetch_related(
            Prefetch('files', queryset=file_queryset)
        ).order_by('-lastmodified_Date')[:20]

        caseSerializer = CaseInfoSearchSerializers(caseDetails, many = True)
        return Response({"responseData":{"response":caseSerializer.data,"status":status.HTTP_200_OK}})

class FileDetailsView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission]
    def put(self, request, pk):
        file = get_object_or_404(FileDetails, pk=pk)
        serializer = FileDetailsUpdateSerializer(file, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "File details updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubmitDraftAPIView(APIView):
    def post(self, request):
        try:
            case_info_json = request.data.get("caseDetails")
            file_details = request.data.get("fileDetails")
            division_id = request.data.get("division_id")
            uploaded_files = request.FILES.getlist("Files")

            if not case_info_json:
                return Response({"error": "No case details provided"}, status=status.HTTP_400_BAD_REQUEST)

            case_data = json.loads(case_info_json) if isinstance(case_info_json, str) else case_info_json
            file_details_data = json.loads(file_details) if file_details else []
            case_details_id = case_data.get("CaseInfoDetailsId")
            print("case_details_id",case_details_id)
            if not division_id:
                return Response({"error": "Division ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            file_changes = []
            case_changes = {}

            # Update if case details id  exists
            if case_details_id:
                print("hey i'm in if block")
                try:
                    case_instance = CaseInfoDetails.objects.get(pk=case_details_id)
                    print("case_instance",case_instance)
                except CaseInfoDetails.DoesNotExist:
                    return Response({"error": "case Draft not found"}, status=status.HTTP_404_NOT_FOUND)
                
                for field, new_val in case_data.items():
                        if hasattr(case_instance, field):
                            old_val = getattr(case_instance, field)
                            if str(old_val) != str(new_val):
                                case_changes[field] = {"old": old_val, "new": new_val}
                                setattr(case_instance, field, new_val)
                
                case_instance.is_draft = False
                case_instance.division = division_id
                case_instance.submitted_at = timezone.now()
                case_instance.lastmodified_by = request.user
                case_instance.lastmodified_Date = timezone.now()
                case_instance.save()

                # Handle file updates
                division_name = Division.objects.get(divisionId=division_id).divisionName
                existing_files = FileDetails.objects.filter(caseDetails=case_instance)
                existing_hashes = {f.fileHash: f for f in existing_files}
                incoming_hashes = set()

                # Process uploaded files: add new ones or skip duplicates
                for i in range(len(uploaded_files)):
                    file_content = uploaded_files[i].read()
                    file_hash = hashlib.sha256(file_content).hexdigest()
                    incoming_hashes.add(file_hash)

                    if file_hash not in existing_hashes:
                        file_name = uploaded_files[i].name
                        file_path = os.path.join(
                            UPLOAD_DIR, str(case_instance.year), division_name,
                            str(case_instance.caseType), case_instance.caseNo,
                            str(file_details_data[i]['fileType']),
                            str(file_details_data[i]['documentType']),
                            file_name
                        )
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, "wb") as f:
                            f.write(file_content)

                        file_obj = FileDetails.objects.create(
                            caseDetails=case_instance,
                            fileName=file_name,
                            filePath=file_path,
                            fileHash=file_hash,
                            subject=file_details_data[i]['subject'],
                            fileType=GeneralLookUp.objects.get(lookupId=file_details_data[i]['fileType']),
                            classification=GeneralLookUp.objects.get(lookupId=file_details_data[i]['classification']),
                            uploaded_by=request.user,
                            division=Division.objects.get(divisionId=division_id),
                            documentType=GeneralLookUp.objects.get(lookupId=file_details_data[i]['documentType'])
                        )
                        record_file_access(request.user, file_obj)
                        file_changes.append({"file": file_name, "action": "added"})
                    else:
                        uploaded_files[i].seek(0)

                # Delete removed files
                for hash_val, file_obj in existing_hashes.items():
                    if hash_val not in incoming_hashes:
                        if os.path.exists(file_obj.filePath):
                            os.remove(file_obj.filePath)
                        file_changes.append({"file": file_obj.fileName, "action": "deleted"})
                        file_obj.delete()
            else:
                print("hey request is in else block :)")
                case_data['division'] = division_id
                # Create new case
                serializer = CaseInfoDetailsSerializer(data=case_data)

                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                case_instance = serializer.save(
                    lastmodified_by=request.user,
                    is_draft=False,
                    submitted_at=timezone.now()
                )

                if not uploaded_files:
                    return Response({"error": "No files uploaded"}, status=status.HTTP_400_BAD_REQUEST)

                division_name = Division.objects.get(divisionId=division_id).divisionName

                for i in range(len(uploaded_files)):
                    file_content = uploaded_files[i].read()
                    file_hash = hashlib.sha256(file_content).hexdigest()

                    file_name = uploaded_files[i].name
                    file_path = os.path.join(
                        UPLOAD_DIR, str(case_instance.year), division_name,
                        str(case_instance.caseType), case_instance.caseNo,
                        str(file_details_data[i]['fileType']),
                        str(file_details_data[i]['documentType']),
                        file_name
                    )
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(file_content)

                    file_obj = FileDetails.objects.create(
                        caseDetails=case_instance,
                        fileName=file_name,
                        filePath=file_path,
                        fileHash=file_hash,
                        hashTag = file_details_data[i]['hashTag'],
                        subject=file_details_data[i]['subject'],
                        fileType=GeneralLookUp.objects.get(lookupId=file_details_data[i]['fileType']),
                        classification=GeneralLookUp.objects.get(lookupId=file_details_data[i]['classification']),
                        uploaded_by=request.user,
                        division=Division.objects.get(divisionId=division_id),
                        documentType=GeneralLookUp.objects.get(lookupId=file_details_data[i]['documentType'])
                    )
                    record_file_access(request.user, file_obj)

            response_data = {
                "message": "Submitted successfully",
                "caseChanges": case_changes,
                "caseDetails": CaseInfoDetailsSerializer(case_instance).data
            }
            # Add fileChanges only for draft submissions
            if case_details_id:
                response_data["fileChanges"] = file_changes

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CaseInfoDraftDetailsView(APIView):
    def get(self, request):
        caseDetails = CaseInfoDetails.objects.filter(is_draft=True)
        serializer = CaseInfoDetailsSerializer(caseDetails, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CaseInfoDetailsView(APIView):
    
    permission_classes = [IsAuthenticated, HasRequiredPermission]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            case_info_json = request.data.get("caseDetails")
            file_details = request.data.get("fileDetails")
            is_draft = request.data.get("is_draft", True)

        
            if not case_info_json:
                return Response({
                    "responseData":{
                        "error":"No Case Details",
                        "status":status.HTTP_400_BAD_REQUEST
                        }
                    })
            
            if isinstance(case_info_json, str):
                case_data = json.loads(case_info_json)
            else:
                case_data = case_info_json


            if isinstance(file_details, str):
                file_details_data = json.loads(file_details)
            else:
                file_details_data = file_details

            division_id = request.data.get("division_id")
            if not division_id:
                return Response({"error": "Division ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
            case_data['division'] = division_id 
            case_data['is_draft'] = is_draft 

            if not is_draft:
                case_data['submitted_at'] = timezone.now()

            case_serailizer = CaseInfoDetailsSerializer(data = case_data)
            if not case_serailizer.is_valid():
                return Response(case_serailizer.errors, status=status.HTTP_400_BAD_REQUEST)

            case_info = case_serailizer.save(lastmodified_by= request.user)


            uploaded_files = request.FILES.getlist("Files")

            if not is_draft and not uploaded_files:
                return Response({"error": "No files Uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            file_details_list = [] 
           
            if uploaded_files:
                div_name=Division.objects.get(divisionId=division_id)

                for i in range(len(uploaded_files)):
                    file_content = uploaded_files[i].read()

                    # Compute file hash (SHA-256)
                    file_hash = hashlib.sha256(file_content).hexdigest()
                    
                    # Define file path and save file
                    file_name = uploaded_files[i].name
                    file_path = os.path.join(
                        UPLOAD_DIR,
                        str(case_info.year),
                        str(div_name.divisionName),
                        str(case_info.caseType),
                        str(case_info.caseNo),
                        str(file_details_data[i]['fileType']),
                        str(file_details_data[i]['documentType']),
                        file_name
                    )

                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    # Write file to disk
                    with open(file_path, "wb") as f:
                        f.write(file_content)

                    # Save file details in the database with casedetailsid
                    file_detail = FileDetails.objects.create(
                        caseDetails=case_info,
                        fileName=file_name,
                        filePath=file_path,
                        fileHash=file_hash,
                        hashTag = file_details_data[i]['hashTag'],
                        subject = file_details_data[i]['subject'],
                        fileType = GeneralLookUp.objects.get(lookupId=file_details_data[i]['fileType']),
                        classification = GeneralLookUp.objects.get(lookupId=file_details_data[i]['classification']),
                        uploaded_by = request.user,
                        division = Division.objects.get(divisionId=request.data.get('division_id')),
                        documentType =GeneralLookUp.objects.get(lookupId=file_details_data[i]['documentType'])
                    )

                    record_file_access(request.user, file_detail)

                    file_details_list.append({
                        "file":FileDetailsSerializer(file_detail).data
                    })
            
            return Response({
                    "caseDetails": CaseInfoDetailsSerializer(case_info).data
                },status=status.HTTP_201_CREATED)

        except Exception as e:
            tb = traceback.format_exc()
            return Response({"error": str(e),"traceback": tb}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self,request,pk):
        try:
            case_details = get_object_or_404(CaseInfoDetails, pk=pk)
            case_info_json = request.data.get("caseDetails")
            file_details = request.data.get("fileDetails")

            if not case_info_json:
                return Response({"error": "No Case Details provided"}, status=status.HTTP_400_BAD_REQUEST)

            if isinstance(case_info_json, str):
                case_data = json.loads(case_info_json)

            if isinstance(file_details, str):
                file_details_data = json.loads(file_details)

            # Update case details
            serializer = CaseInfoDetailsSerializer(case_details, data=case_data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            caseInfo = serializer.save()

            uploaded_files = request.FILES.getlist("Files")
            new_file_index = 0  # Index tracker for new file uploads
            file_responses = []

            for file_detail in file_details_data:
                file_id = file_detail.get("fileId")
                new_hashtag = file_detail.get("hashTag")
                new_subject = file_detail.get("subject")
                new_classification = file_detail.get("classification")
                new_fileType = file_detail.get("fileType")


                if file_id:
                    # Update existing file
                    try:
                        file_obj = FileDetails.objects.get(pk=file_id, caseDetails=case_details)
                        file_obj.hashTag = new_hashtag
                        file_obj.subject = new_subject
                        file_obj.classification = new_classification
                        file_obj.fileType = new_fileType

                        file_obj.save()

                        file_responses.append({
                            "file": FileDetailsSerializer(file_obj).data,
                            "status": "updated"
                        })
                    except FileDetails.DoesNotExist:
                        continue
                else:
                    # Add new file
                    if new_file_index >= len(uploaded_files):
                        return Response({"error": "fileDetails and uploaded Files doesn't match"}, status=status.HTTP_400_BAD_REQUEST)

                    uploaded_file = uploaded_files[new_file_index]
                    file_content = uploaded_file.read()
                    file_hash = hashlib.sha256(file_content).hexdigest()
                    file_name = uploaded_file.name
                    file_path = os.path.join(UPLOAD_DIR, file_name)

                    # Save file to disk
                    with open(file_path, "wb") as f:
                        f.write(file_content)

                    new_file = FileDetails.objects.create(
                        caseDetails=caseInfo,
                        fileName=file_name,
                        filePath=file_path,
                        fileHash=file_hash,
                        hashTag=new_hashtag,
                        subject = new_subject,
                        fileType = new_fileType,
                        classification = new_classification,
                        uploaded_by=request.user
                    )

                    record_file_access(request.user, new_file)

                    file_responses.append({
                        "file": FileDetailsSerializer(new_file).data,
                        "status": "created"
                    })

                    new_file_index += 1
            return Response(
                {
                    "caseDetails": CaseInfoDetailsSerializer(caseInfo).data,
                    "files": file_responses,
                    "message": "Case details and files processed successfully."
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CaseFileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, casedetailsId):
        try:
            caseData = get_object_or_404(CaseInfoDetails, pk=casedetailsId)
            file_details_json = request.data.get("fileDetails")

            if isinstance(file_details_json, str):
                file_details_data = json.loads(file_details_json)

            files = request.FILES.getlist("Files")
            if not files:
                return Response({"error": "No files uploaded"}, status=400)
            
            if len(files) != len(file_details_data):
                return Response({"error": "Mismatch between file details and files"}, status=400)

            file_responses = []
            for i, file in enumerate(files):
                content = file.read()
                file_hash = hashlib.sha256(content).hexdigest()

                if FileDetails.objects.filter(fileHash=file_hash, caseDetails=caseData).exists():
                    continue  # skip duplicate

                file_name = file.name
                file_path = os.path.join(UPLOAD_DIR, file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as f:
                    f.write(content)

                file_detail = FileDetails.objects.create(
                    caseDetails=caseData,
                    fileName=file_name,
                    filePath=file_path,
                    fileHash=file_hash,
                    hashTag=file_details_data[i]["hashTag"],
                    subject=file_details_data[i]["subject"],
                    fileType=GeneralLookUp.objects.get(lookupId=file_details_data[i]["fileType"]),
                    classification=GeneralLookUp.objects.get(lookupId=file_details_data[i]["classification"]),
                    documentType=GeneralLookUp.objects.get(lookupId=file_details_data[i]["documentType"]),
                    uploaded_by=request.user,
                    division=caseData.division
                )

                record_file_access(request.user, file_detail)
                file_responses.append(FileDetailsSerializer(file_detail).data)

            return Response({
                "files": file_responses,
                "message": "Files uploaded successfully"
            }, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
def convert_docx_to_pdf(docx_path):
    output_dir = os.path.dirname(docx_path)
    convert(docx_path, output_dir)
    return os.path.splitext(docx_path)[0] + '.pdf'

class FilePreviewAPIView(APIView):
    permission_classes = [IsAuthenticated, HasCustomPermission]
    required_permission = 'add_filepreviewapi'

    def post(self, request):
        file_hash = request.data.get("fileHash")
        requested_to_id = request.data.get("requested_to")
        comments = request.data.get("comments")
        case_id = request.data.get("case_id")
        division_id = request.data.get("division_id")

        if not file_hash or not case_id:
            return Response({
                "responseData": {
                    "error": "fileHash and case details id are required",
                    "status": status.HTTP_400_BAD_REQUEST
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            objFile = FileDetails.objects.select_related('classification').get(fileHash=file_hash, 
                                                                               caseDetails_id = case_id )
            filePath = objFile.filePath
            file_ext = os.path.splitext(filePath)[1].lower()

            user_role_id = request.user.role.roleId

            # Direct access if user is uploader, Admin, or Viewer
            if request.user != objFile.uploaded_by and user_role_id not in [1, 3]:
                if objFile.classification_id==6:
                    is_approved = FileAccessRequest.objects.filter(file=objFile, requested_by=request.user,
                                    is_approved=True, division_id=objFile.division_id).exists()
                    
                    if not is_approved:
                        already_requested = FileAccessRequest.objects.filter(
                            file=objFile,
                            requested_by=request.user,
                            division_id=objFile.division_id
                        ).exists()

                        if not already_requested:
                            if not requested_to_id:
                                return Response({
                                    "responseData": {
                                        "error": "requested_to is required for private files",
                                        "status": status.HTTP_400_BAD_REQUEST
                                    }
                                }, status=status.HTTP_400_BAD_REQUEST)
                            
                        requested_to_user = get_object_or_404(User, id=requested_to_id)
                        FileAccessRequest.objects.create(
                            file=objFile,
                            requested_by=request.user,
                            requested_to=requested_to_user,
                            comments = comments,
                            division_id=objFile.division_id,
                            reviewed_by = requested_to_user,
                            case_details_id = CaseInfoDetails.objects.get(CaseInfoDetailsId=case_id)
                        )

                        return Response({
                            "responseData": {
                                "message": "Access request sent. Waiting for approval.",
                                "status": status.HTTP_202_ACCEPTED
                            }
                        })
                    
            record_file_access(request.user, objFile)
            
            if not os.path.exists(filePath):
                    raise FileNotFoundError("File not found on disk")
            
            # if file_ext in ['.png', '.jpg', '.jpeg', '.pdf', '.mp4', '.webm', '.mp3', '.wav']:
            #     mime_type, _ = mimetypes.guess_type(filePath)
            #     response = FileResponse(open(filePath, 'rb'), content_type=mime_type or 'application/octet-stream')
            #     response['Content-Disposition'] = 'inline; filename="{}"'.format(os.path.basename(filePath))
            #     return response
            
            # elif file_ext == '.docx':
            #     print(filePath)
            #     pdf_path = convert_docx_to_pdf(filePath)

            #     if not os.path.exists(pdf_path):
            #         raise FileNotFoundError("PDF conversion failed or file not found.")

            #     return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
            # elif file_ext == '.docx':
            #     with open(filePath, "rb") as docx_file:
            #         result = mammoth.convert_to_html(docx_file)
            #         html_content = result.value
            #         return Response({
            #             "type": "html",
            #             "html": html_content
            #         }, status=200)

            # elif file_ext == '.xlsx':
            #     print(filePath)
            #     df = pd.read_excel(filePath)
            #     html_table = df.to_html(index=False, border=0)
            #     html_content = f"""
            #         <style>
            #         table {{
            #             border-collapse: collapse;
            #             width: 100%;
            #             font-family: Arial, sans-serif;
            #         }}
            #         th, td {{
            #             border: 1px solid #ddd;
            #             padding: 8px 12px;
            #             text-align: left;
            #             white-space: nowrap;
            #         }}
            #         tr:nth-child(even) {{ background-color: #f9f9f9; }}
            #         tr:hover {{ background-color: #f1f1f1; }}
            #         </style>
            #         <div style="overflow-x:auto;">
            #         {html_table}
            #         </div>
            #         """
            #     return Response({
            #         "type": "html",
            #         "html": html_content
            #     }, status=200)

            # else:
            #     return Response({
            #         "responseData": {
            #             "error": "Unsupported file type for preview",
            #             "status": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            #         }
            #     }, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            with open(filePath, 'rb') as f:
                encoded_file = base64.b64encode(f.read()).decode('utf-8')
                mime_type, _ = mimetypes.guess_type(filePath)

            return Response({
                "type": "base64",
                "mime_type": mime_type or 'application/octet-stream',
                "file_name": os.path.basename(filePath),
                "base64_content": encoded_file
            }, status=200)
            
        except FileDetails.DoesNotExist:
            raise Http404("File not found")

        except FileNotFoundError:
            raise Http404("File missing from server")

      
  
class FileAccessRequestListAPIView(APIView):
    # queryset = FileAccessRequest.objects.all().order_by('-created_at')
    # serializer_class = FileAccessRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user = request.user
        division_id = request.data.get("division_id")

        approvals = FileAccessRequest.objects.all()

        print("division_id",division_id)
        if user.role.roleId == 3:  # Content manager role
            # Viewer can also see the approvals where they are assigned for review
            approvals = approvals.filter(reviewed_by=user)
        else:  # Regular User
            # Regular user can only see the requests they have submitted
            approvals = approvals.filter(requested_by=user)

        if division_id:
            approvals = approvals.filter(file__division__divisionId=division_id)

        # Optional: Filter by department_id if needed
        # if department_id:
        #     approvals = approvals.filter(file__division__departmentId=department_id)

        # Content Managers can see requests where they are the requested_to user
        serializer = FileAccessRequestSerializer(approvals, many=True)

        return Response(serializer.data)

class RevokeFileAccessRequestAPIView(APIView):
    permission_classes = [IsAuthenticated,FileDetailsPermission]

    def post(self, request, *args, **kwargs):
        request_id = request.data.get("request_id")
        division_id = request.data.get("division_id")
        comments = request.data.get("comments")
        
        if not request_id or not division_id:
            return Response({"error": "Missing request_id or division_id"}, status=status.HTTP_400_BAD_REQUEST)

        file_request = get_object_or_404(FileAccessRequest, id=request_id)
        user = request.user

        # Check if user has the right role
        try:
            user_division = UserDivisionRole.objects.get(user=user, division=division_id)
        except UserDivisionRole.DoesNotExist:
            return Response({"error": "User does not have access to this division"}, status=status.HTTP_403_FORBIDDEN)

        file_request.is_approved=False
        file_request.comments = comments
        # Revoke the request
        file_request.status = "revoked"  # You can define a 'revoked' status in your choices
        file_request.save()

        file_Details_object= FileDetails.objects.get(fileId = file_request.file_id)
        file_Details_object.is_approved=False
        print('file_Details_object',file_Details_object.is_approved)
        return Response({"message": "File access request revoked successfully"}, status=status.HTTP_200_OK)
    
class ApproveorDenyConfidentialAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        is_approved = request.data.get('is_approved')
        comment = request.data.get('comment', '')
        revoke_enddate = request.data.get('end_date',None) 

        access_request = get_object_or_404(FileAccessRequest, pk=pk)

        if is_approved not in [True, False, 'true', 'false', 'True', 'False', 1, 0]:
            return Response({
                "responseData": {
                    "error": "is_approved must be true or false",
                    "status": status.HTTP_400_BAD_REQUEST
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        is_approved_bool = str(is_approved).lower() == 'true' or is_approved == 1


        access_request.is_approved = is_approved_bool
        access_request.status = "Approved" if is_approved_bool else "Denied"
        access_request.comment = comment
        access_request.approved_by = request.user
        access_request.approved_at = timezone.now()
        access_request.revoke_startdate= timezone.now()
        access_request.revoke_enddate = revoke_enddate
        access_request.save()

        if is_approved_bool:
            file_obj = access_request.file
            file_obj.is_approved = True
            file_obj.save()

        Notification.objects.filter(
            type="ACCESS_REQUEST",
            object_id=access_request.id,
            content_type=ContentType.objects.get_for_model(FileUploadApproval),
        ).update(is_read=True, read_at=timezone.now())

        Notification.objects.create(
            recipient=access_request.requested_by,
            requestedBy=request.user,
            division=access_request.division,
            message=f"Your file has been {'approved' if is_approved else 'denied'} with comments: {comment}",
            type="GENERIC",
            content_type=ContentType.objects.get_for_model(FileUploadApproval),
            object_id=access_request.id
        )
        

        return Response({
            "responseData": {
                "message":f"Request {'approved' if is_approved_bool else 'denied'} successfully.",
                "status": status.HTTP_200_OK
            }
        }, status=status.HTTP_200_OK)
    
class SendUploadApprovalReminder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,approval_id):
        approval = get_object_or_404(FileUploadApproval, id=approval_id)

        # logic to check only the uploaded users can send reminder
        if approval.requested_by != request.user:
            return Response({"error": "Only the uploader can send reminders."}, status=403)
        
        if approval.status != "PENDING":
            return Response({"error": "Approval is not pending."}, status=400)
        
        content_type = ContentType.objects.get_for_model(FileUploadApproval)

        last_reminder = Notification.objects.filter(
            type='UPLOAD_APPROVAL_REMINDER',
            content_type=content_type,
            object_id=approval.id,
            requestedBy=request.user
        ).order_by('-created_at').first()

        if last_reminder and (timezone.now() - last_reminder.created_at < timedelta(days=1)):
            return Response({
                "error": "Reminder already sent recently. can send a reminder again next day."
            }, status=400)
        
        
        reviewer = approval.reviewed_by

        if reviewer:
            Notification.objects.create(
                recipient=reviewer,
                requestedBy=request.user,
                message=(
                    f"Reminder: {request.user.first_name} uploaded a file for approval "
                    f"(Case: {approval.file.caseDetails.caseNo})"
                ),
                type='UPLOAD_APPROVAL_REMINDER',
                content_type=content_type,
                object_id=approval.id,
                division = approval.division
            )

        return Response({"message": "Reminder sent successfully."})

class SendAccessApprovalReminder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,access_id):
        approval = get_object_or_404(FileAccessRequest, id=access_id)

        # logic to check only the uploaded users can send reminder
        if approval.requested_by != request.user:
            return Response({"error": "Only the uploader can send reminders."}, status=403)
        
        if approval.status != "pending":
            return Response({"error": "Only for pending files reminders can be sent."}, status=400)
        
        content_type = ContentType.objects.get_for_model(FileAccessRequest)

        last_reminder = Notification.objects.filter(
            type='ACCESS_REQUEST_REMINDER',
            content_type=content_type,
            object_id=approval.id,
            requestedBy=request.user
        ).order_by('-created_at').first()

        if last_reminder and (timezone.now() - last_reminder.created_at < timedelta(days=1)):
            return Response({
                "error": "Reminder already sent recently. can send a reminder again next day."
            }, status=400)
        
        
        reviewer = approval.reviewed_by

        if reviewer:
            Notification.objects.create(
                recipient=reviewer,
                requestedBy=request.user,
                message=(
                    f"Reminder: {request.user.first_name} Requested access for a file uploaded in "
                    f"(Case: {approval.file.caseDetails.caseNo})"
                ),
                type='ACCESS_REQUEST_REMINDER',
                content_type=content_type,
                object_id=approval.id,
                division = approval.division
            )

        return Response({"message": "Reminder sent successfully."})
    
class WithdrawUploadApprovalView(APIView):
    def post(self, request, approval_id):
        approval = get_object_or_404(FileUploadApproval, id=approval_id, requested_by=request.user)

        if approval.requested_by != request.user:
            return Response({"error": "Only the uploader can withdraw requests."}, status=403)
        
        if approval.status != 'PENDING':
            return Response({"error": "Only pending approvals can be withdrawn."}, status=400)

        file_detail = approval.file

        # Delete related notifications
        Notification.objects.filter(
            content_type=ContentType.objects.get_for_model(approval),
            object_id=approval.id,
            type__in=['UPLOAD_APPROVAL', 'UPLOAD_APPROVAL_REMINDER']
        ).delete()

        # Delete file from disk and database
        if file_detail:
            file_path = file_detail.filePath
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
            file_detail.delete()

        # # Now update the approval
        # approval.status = 'WITHDRAWN'
        # approval.file = None  # ← Set to None before saving, to prevent the error
        # approval.save()
        approval.delete()

        return Response({"message": "Upload approval Request withdrawn successfully."})

class WithdrawAccessApprovalView(APIView):
    def post(self, request, access_id):
        approval = get_object_or_404(FileAccessRequest, id=access_id, requested_by=request.user)

        if approval.requested_by != request.user:
            return Response({"error": "Only the uploader can withdraw requests."}, status=403)
        
        if approval.status != 'pending':
            return Response({"error": "Only pending approvals can be withdrawn."}, status=400)

        file_detail = approval.file

        # Delete related notifications
        Notification.objects.filter(
            content_type=ContentType.objects.get_for_model(approval),
            object_id=approval.id,
            type__in=['UPLOAD_APPROVAL', 'UPLOAD_APPROVAL_REMINDER']
        ).delete()


        # # Now update the approval
        # approval.status = 'WITHDRAWN'
        # approval.file = None  # ← Set to None before saving, to prevent the error
        # approval.save()
        approval.delete()

        return Response({"message": "Upload approval Request withdrawn successfully."})
      
class UploadApprovalListView(APIView):
    def post(self, request):
        user = request.user
        division_id = request.data.get('division_id')
        department_id = request.data.get('department_id')

        # Start with all the pending approvals
        approvals = FileUploadApproval.objects.all()

        # Fetch the designations based on the division_id
        designations = Designation.objects.filter(division__divisionId=division_id)
        print('designations- approval method', designations)

        # Check if the logged-in user is an Admin (role_id = 1), Viewer (role_id = 4), or regular user
        if user.role.roleId == 1:  # Admin role
            # Admin can see all approvals where they are assigned for review
            approvals = approvals.filter(reviewed_by=user)
        elif user.role.roleId == 3:  # content manager role
            # Viewer can also see the approvals where they are assigned for review
            approvals = approvals.filter(reviewed_by=user)
        else:  # Regular User
            # Regular user can only see the requests they have submitted
            approvals = approvals.filter(requested_by=user)

        # Filter by division if provided
        if division_id:
            approvals = approvals.filter(file__division__divisionId=division_id)

        # Optional: Filter by department_id if needed
        if department_id:
            approvals = approvals.filter(file__division__departmentId=department_id)

        # Serialize and return the data
        serializer = FileUploadApprovalSerializer(approvals, many=True)
        return Response(serializer.data)
    
class UploadApprovalDetailView(RetrieveAPIView):
    queryset = FileUploadApproval.objects.all()
    serializer_class = FileUploadApprovalSerializer
    lookup_field = 'id' 

class FileApprovalDetailsViewSet(APIView):
   permission_classes=[IsAuthenticated]
   def post(self, request):
        upload_approval_id = request.data.get("upload_approval_id")
        is_approved= request.data.get("is_approved")
        comments = request.data.get("comments")

        upload_approval = get_object_or_404(FileUploadApproval, id=upload_approval_id)
        file = upload_approval.file

        file.is_approved = is_approved
        file.comments = comments
        file.save(update_fields=["is_approved", "comments"])

        upload_approval.status = "APPROVED" if is_approved else "DENIED"
        upload_approval.is_approved = is_approved
        upload_approval.reviewed_by = request.user
        upload_approval.reviewed_at = timezone.now()
        upload_approval.approved_by=request.user
        upload_approval.save()
        
        Notification.objects.filter(
            type="UPLOAD_APPROVAL",
            object_id=upload_approval.id,
            content_type=ContentType.objects.get_for_model(FileUploadApproval),
        ).update(is_read=True, read_at=timezone.now())

        other_pending_approvals = FileUploadApproval.objects.filter(
            file=file,
            status="PENDING"
        ).exclude(id=upload_approval.id)

        other_pending_approvals.update(status = "APPROVED" if is_approved else "DENIED",reviewed_at = timezone.now(),is_approved = is_approved,
                                       approved_by=request.user)

        for other_approval in other_pending_approvals:
            Notification.objects.filter(
                type="UPLOAD_APPROVAL",
                object_id=other_approval.id,
                content_type=ContentType.objects.get_for_model(FileUploadApproval),
            ).update(is_read=True, read_at=timezone.now())

        Notification.objects.create(
            recipient=upload_approval.requested_by,
            requestedBy=request.user,
            division=file.division,
            message=f"Your file has been {'approved' if is_approved else 'denied'} with comments: {comments}",
            type="GENERIC",
            content_type=ContentType.objects.get_for_model(FileUploadApproval),
            object_id=upload_approval.id
        )
        return Response({"status": "File Processed"}, status=status.HTTP_200_OK)

class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        division_id = request.query_params.get('division_id')
        allowed_types = ["UPLOAD_APPROVAL", "ACCESS_REQUEST", "GENERIC", "UPLOAD_APPROVAL_REMINDER"]

        if not division_id and not user.is_staff:
            return Response({"detail": "Division ID is required."}, status=400)
        
        if user.is_staff:
            notifications = Notification.objects.filter(
                recipient=user,
                type__in=allowed_types
            ).order_by('-created_at').distinct()
        else:
            notifications = Notification.objects.filter(
                recipient=user,
                division__divisionId=division_id,
                type__in=allowed_types
            ).order_by('-created_at')
       

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MarkNotificationAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        notification_id = request.data.get("notification_id")

        if not notification_id:
            return Response({"error": "Notification ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        notification = get_object_or_404(Notification, id=notification_id)

        # Check if the user is allowed to mark it as read
        if request.user != notification.recipient and not request.user.is_staff:
            return Response({"error": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        notification.is_read = True
        notification.save()

        return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)