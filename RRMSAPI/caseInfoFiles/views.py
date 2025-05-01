from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CaseInfoDetailsSerializer,FileAccessRequestSerializer,FileDetailsSerializer,NotificationSerializer, CaseInfoSearchSerializers, FavouriteSerializer
from .models import FileDetails, CaseInfoDetails, FavouriteFiles, Notification, FileAccessRequest
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, OuterRef, Exists, Case, When, Value, BooleanField
from .utils import record_file_access, timezone
from django.conf import settings
from django.db.models import Q
from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from mdm.permissions import HasRequiredPermission
from mdm.models import FileClassification, FileType, DivisionMaster
from users.models import UserDivisionRole
from rest_framework.parsers import MultiPartParser, FormParser
from .permissions import HasCustomPermission,FileDetailsPermission
from rest_framework.generics import ListAPIView
from django.contrib.auth import get_user_model
import json
import hashlib
import os
import mimetypes
import traceback

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads","CID")
os.makedirs(UPLOAD_DIR, exist_ok=True)

User = get_user_model()

# Create your views here.
class LatestUserFilesView(ListAPIView):
    serializer_class = FileDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FileDetails.objects.filter(uploaded_by=self.request.user).order_by('-created_at')[:20]  # Adjust limit as needed


class FavouriteFilesView(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermission]

    def get(self,request):
        division_id = request.query_params.get("division_id")
        favs= FavouriteFiles.objects.filter(user=request.user,division_id=division_id).order_by('-added_at')
        serializer = FavouriteSerializer(favs, many=True)
        return Response(serializer.data)

    def post(self, request, file_id):
        division_id = request.query_params.get("division_id")
        division = DivisionMaster.objects.get(divisionId = division_id)
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

        if "division_id" in searchParams:
            query |= Q(division__divisionId__icontains= searchParams['division_id'])

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

        user_divisions= UserDivisionRole.objects.get(user = user, division_id = searchParams['division_id'])
        if user.is_staff or user_divisions.role == 4 or user_divisions.role == 1:
            file_filter = Q()  # Admin sees all
        else:
            request_raised_subquery = FileAccessRequest.objects.filter(
                file=OuterRef('pk'),
                requested_by=user
                )
            access_request_subquery = FileAccessRequest.objects.filter(
                file=OuterRef('pk'),
                requested_by=user,
                is_approved=True 
                )
            file_filter = Q(is_approved=True) | Q(uploaded_by=user) | Exists(access_request_subquery)

        favourite_subquery = FavouriteFiles.objects.filter(user=request.user,file=OuterRef('pk'))
        print("access- ",file_filter)
        file_queryset = FileDetails.objects.select_related('classification').filter(file_filter).annotate(
            is_favourited=Exists(favourite_subquery),
            is_request_raised = Exists(request_raised_subquery),
            is_access_request_approved=Exists(access_request_subquery)
            )

        caseDetails = case_details_qs.prefetch_related(
            Prefetch('files', queryset=file_queryset)
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

            division_id = request.data.get("division_id")
            if not division_id:
                return Response({"error": "Division ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
            case_data['division'] = division_id 
            case_serailizer = CaseInfoDetailsSerializer(data = case_data)

            if not case_serailizer.is_valid():
                return Response(case_serailizer.errors, status=status.HTTP_400_BAD_REQUEST)

            caseInfo = case_serailizer.save(lastmodified_by= request.user)

            div_name=DivisionMaster.objects.get(divisionId=division_id)

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
                file_path = os.path.join(UPLOAD_DIR, str(caseInfo.year),str(div_name.divisionName), str(caseInfo.caseNo),str(file_details_data[i]['fileStage']),file_name)

                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                # Write file to disk
                with open(file_path, "wb") as f:
                    f.write(file_content)

                # Save file details in the database with casedetailsid
                file_detail = FileDetails.objects.create(
                    caseDetails=caseInfo,
                    fileName=file_name,
                    filePath=file_path,
                    fileHash=file_hash,
                    hashTag = file_details_data[i]['hashTag'],
                    subject = file_details_data[i]['subject'],
                    fileType = FileType.objects.get(fileTypeId=file_details_data[i]['fileType']),
                    classification = FileClassification.objects.get(fileClassificationId=file_details_data[i]['classification']),
                    uploaded_by = request.user,
                    division = DivisionMaster.objects.get(divisionId=request.data.get('division_id')),
                    filestage =file_details_data[i]['fileStage']
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

class FilePreviewAPIView(APIView):
    permission_classes = [IsAuthenticated, HasCustomPermission]
    required_permission = 'add_filepreviewapi'

    def post(self, request):
        file_hash = request.data.get("fileHash")
        requested_to_id = request.data.get("requested_to")
        comments = request.data.get("comments")
        case_id = request.data.get("case_id")
        division_id = request.data.get("division_id")

        if not file_hash:
            return Response({
                "responseData": {
                    "error": "fileHash is required",
                    "status": status.HTTP_400_BAD_REQUEST
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            objFile = FileDetails.objects.select_related('classification').get(fileHash=file_hash, caseDetails_id = case_id )
            filePath = objFile.filePath
            user_division_ids = request.user.userdivisionrole_set.values_list('division_id', flat=True)


            if objFile.classification_id == 12 and objFile.uploaded_by_id != request.user.id and objFile.division_id in user_division_ids:

                # Check if user already has access
                is_approved = FileAccessRequest.objects.filter(
                    file=objFile,
                    requested_by=request.user,
                    is_approved=True,
                    division_id=objFile.division_id
                ).exists()

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

                        requested_to_id = request.data.get("requested_to")
                        requested_to_user = get_object_or_404(User, id=requested_to_id)
                        access_request = FileAccessRequest.objects.create(
                            file=objFile,
                            requested_by=request.user,
                            requested_to=requested_to_user,
                            comments = comments,
                            division_id=objFile.division_id
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

            mime_type, _ = mimetypes.guess_type(filePath)
            return FileResponse(open(filePath, 'rb'), content_type=mime_type or 'application/octet-stream')

        except FileDetails.DoesNotExist:
            raise Http404("No file with given hash")

        except FileNotFoundError:
            raise Http404("File path invalid or missing")
  
class FileAccessRequestListAPIView(ListAPIView):
    queryset = FileAccessRequest.objects.all().order_by('-created_at')
    serializer_class = FileAccessRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        division_id = self.request.query_params.get("division_id")

        user_divisions= UserDivisionRole.objects.get(user = user, division = division_id)
        print("division_id",division_id)
        if user.is_superuser or user_divisions.role_id == 1:  # assuming role_id=1 is admin
            return FileAccessRequest.objects.all().order_by('-created_at')

        # Content Managers can see requests where they are the requested_to user
        return FileAccessRequest.objects.filter(requested_to=user).order_by('-created_at')

class RevokeFileAccessRequestAPIView(APIView):
    permission_classes = [IsAuthenticated,FileDetailsPermission]

    def post(self, request, *args, **kwargs):
        request_id = request.data.get("request_id")
        division_id = request.data.get("division_id")
        
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
        # Revoke the request
        file_request.status = "revoked"  # You can define a 'revoked' status in your choices
        file_request.save()

        return Response({"message": "File access request revoked successfully"}, status=status.HTTP_200_OK)
    
class ApproveorDenyConfidentialAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        is_approved = request.data.get('is_approved')
        comment = request.data.get('comment', '') 

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
        access_request.save()

        if is_approved_bool:
            file_obj = access_request.file
            file_obj.is_approved = True
            file_obj.save()

        Notification.objects.create(
            recipient=access_request.requested_by,
            message= f"Request {'approved' if is_approved_bool else 'denied'} successfully.",
            file=access_request.file
        )

        return Response({
            "responseData": {
                "message":f"Request {'approved' if is_approved_bool else 'denied'} successfully.",
                "status": status.HTTP_200_OK
            }
        }, status=status.HTTP_200_OK)

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

        division_id = request.query_params.get('division_id')

        if not division_id:
            return Response({"detail": "Division ID is required."}, status=400)
        
        user_division_role = UserDivisionRole.objects.filter(user=user).first()
    
        if user.is_staff:
            notifications = Notification.objects.all().order_by('-created_at')
        elif user_division_role.role_id==1:
            notifications = Notification.objects.filter(division=division_id).order_by('-created_at')
        elif user_division_role.role_id==4:
            user_division = user_division_role.division
            notifications = Notification.objects.filter(
                            recipient=user, division = user_division).order_by('-created_at')
        else:
            return Response({"detail": "Not authorized."}, status=403)

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