from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CaseInfoDetailsSerializer,FileDetailsSerializer,NotificationSerializer, CaseInfoSearchSerializers, FavouriteSerializer
from .models import FileDetails, CaseInfoDetails, FavouriteFiles, Notification
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from .utils import record_file_access
from django.conf import settings
from django.db.models import Q
from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from mdm.permissions import HasRequiredPermission
from rest_framework.parsers import MultiPartParser, FormParser
from .permissions import HasCustomPermission,FileDetailsPermission
from rest_framework.generics import ListAPIView
import json
import hashlib
import os
import mimetypes

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads/")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create your views here.
class LatestUserFilesView(ListAPIView):
    serializer_class = FileDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FileDetails.objects.filter(uploaded_by=self.request.user).order_by('-created_at')[:20]  # Adjust limit as needed


class FavouriteFilesView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission]

    def get(self,request):
        favs= FavouriteFiles.objects.filter(user=request.user).order_by('-added_at')
        serializer = FavouriteSerializer(favs, many=True)
        return Response(serializer.data)

    def post(self, request, file_id):
        try:
            file = FileDetails.objects.get(fileId=file_id)
            print('authenticated user: ',request.user)
            fav, created = FavouriteFiles.objects.get_or_create(user=request.user, file=file)
            if not created:
                record_file_access(request.user, file)
                return Response({'message': 'Already in favorites'}, status=status.HTTP_200_OK)
            return Response({'message': 'Added to favorites'}, status=status.HTTP_201_CREATED)
        except FileDetails.DoesNotExist:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,file_id):
        try:
            fav = FavouriteFiles.objects.get(user = request.user,file_id = file_id)
            file = FileDetails.objects.get(fileId = file_id)
            fav.delete()
            record_file_access(request.user, file)

            return Response({'message':'Removed from favourites'},status= status.HTTP_200_OK)
        except FavouriteFiles.DoesNotExist:
            return Response({'error': 'This file is not favourited'}, status=status.HTTP_404_NOT_FOUND)
  

class SearchCaseFilesView(APIView):
    permission_classes = [HasCustomPermission]
    required_permission = 'view_caseinfodetails'

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

        if "letterNo" in searchParams:
            query |= Q(letterNo__icontains= searchParams['letterNo'])

        if "caseNo" in searchParams:
            query |= Q(caseNo__icontains= searchParams['caseNo'])

        if "firNo" in searchParams:
            query |= Q(firNo__icontains= searchParams['firNo'])

        if "caseDate" in searchParams:
            query |= Q(caseDate__icontains= searchParams['caseDate'])

        if 'hashtag' in searchParams:
            query |= Q(files__hashTag__icontains=searchParams['hashtag'])

        if 'subject' in searchParams:
            query |= Q(files__subject__icontains= searchParams['subject'])

        if 'classification' in searchParams:
            query |= Q(files__classification__icontains= searchParams['classification'])

        if 'fileType' in searchParams:
            query |= Q(files__fileType__icontains= searchParams['fileType'])

        case_details_qs = CaseInfoDetails.objects.filter(query).distinct()

        user = request.user
        if user.is_staff:
            file_filter = Q()  # Admin sees all
        else:
            file_filter = Q(is_approved=True) | Q(uploaded_by=user)

        caseDetails = case_details_qs.prefetch_related(
            Prefetch('files', queryset=FileDetails.objects.filter(file_filter))
        ).order_by('-lastmodified_Date')[:20]

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

            caseInfo = case_serailizer.save(lastmodified_by= request.user)

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
                    classification = file_details_data[i]['classification'],
                    uploaded_by = request.user
                )

                record_file_access(request.user, file_detail)

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

class FilePreviewAPIView(APIView):
    permission_classes = [IsAuthenticated, HasCustomPermission]
    required_permission = 'add_filepreviewapi'
    def post(self,request):
        file_hash = request.data.get("fileHash")

        if not file_hash:
            return Response({"responseData":{"error": "fileHash is required", "status" : status.HTTP_400_BAD_REQUEST}})

        try:
            objFile = FileDetails.objects.get(fileHash = file_hash)
            filePath = objFile.filePath

            record_file_access(request.user, objFile)
            
            if not os.path.exists(filePath):
                raise FileNotFoundError("File not found on disk")

            mime_type, _ = mimetypes.guess_type(filePath)
            return FileResponse(open(filePath, 'rb'), content_type=mime_type or 'application/octet-stream')

        except FileDetails.DoesNotExist:
            raise Http404("No file with given hash")

        except FileNotFoundError:
            raise Http404("File path invalid or missing")


class FileApprovalDetailsViewSet(APIView):
   permission_classes=[FileDetailsPermission]
   def post(self, request, pk):
        file = get_object_or_404(FileDetails, pk=pk)
        file.is_approved = True
        file.save()
        return Response({"status": "File approved"}, status=status.HTTP_200_OK)

class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_staff:
            notifications = Notification.objects.all().order_by('-created_at')
        elif user.role_id==4:
            notifications = Notification.objects.filter(
                            recipient=user).order_by('-created_at')
        else:
            return Response({"detail": "Not authorized."}, status=403)

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)