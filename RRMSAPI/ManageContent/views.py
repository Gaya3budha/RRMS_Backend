import os
from pathlib import Path
from uuid import uuid4
from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework import status
from collections import defaultdict
from django.core.files.storage import default_storage


from ManageContent.utils import nested_dict, user_access_scope
from caseInfoFiles.models import CaseInfoDetails, FileDetails
from mdm.models import Department, Division, GeneralLookUp, UnitMaster
from users.models import User
from django.db import transaction
import re

# Create your views here.
class FolderTreeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        division_id = request.data.get("division_id")
        year=request.data.get("year")
        caseNo=request.data.get("caseNo")
        caseType=request.data.get("caseType")
        fileTypeId=request.data.get("fileTypeId")
        docTypeId=request.data.get("documentTypeId")
        user = request.user

        # if not division_id:
        #     return Response({"detail": "division_id is required"}, status=400)
        
        user_designations = user.designation.all()

        user_division_ids = Division.objects.filter(
            designation__in=user_designations
        ).values_list("divisionId", flat=True).distinct()

        user_department_ids = Department.objects.filter(
            designation__in=user_designations
        ).values_list("departmentId", flat=True).distinct()

        if int(division_id) not in user_division_ids:
            return Response({"detail": "Unauthorized for this division"}, status=403)
        
        # Load relevant files based on user role
        files = FileDetails.objects.select_related("division","caseDetails","fileType","documentType","division__departmentId"
                                                   ).filter(
                                Q(division_id=division_id),
                                Q(division_id__in=user_division_ids) | Q(division__departmentId__in=user_department_ids),
                                isArchieved=False
                            )

        if division_id:
            files = files.filter(division_id=division_id)
        if year:
            files = files.filter(caseDetails__year = int(year))
        if caseNo:
            files = files.filter(caseDetails__caseNo = str(caseNo))
        if caseType:
            files = files.filter(caseType = caseType)
        if fileTypeId:
            files = files.filter(fileType_id = fileTypeId)
        if docTypeId:
            files = files.filter(documentType_id=docTypeId)

        if not division_id:
            # First level: show divisions user has access to
            divisions = files.values("division_id", "division__divisionName").distinct()
            return Response([
                {
                    "id": d["division_id"],
                    "name": d["division__divisionName"],
                    "type": "folder",
                    "level": "division"
                }
                for d in divisions
            ])
        elif division_id and not year:
            yearData=files.values_list("caseDetails__year",flat=True).distinct()
            division_files = files.filter(caseDetails__year__isnull=True)
            return Response({
                "folders":[
                {"name": y, "type": "folder", "level": "year"}
                for y in yearData if y is not None
            ],
            "files":[
                {
                    "file_id": f.fileId,
                    "name": f.fileName,
                    "path":  request.build_absolute_uri(f.filePath) if f.filePath else None,
                    "created_at": f.created_at,
                    "uploaded_by": f.uploaded_by.first_name + ' ' + f.uploaded_by.last_name if f.uploaded_by else None
                }
                for f in division_files
            ]
            })
        elif division_id and year and not caseNo:
            # Return caseno as folders
            caseData = files.values_list("caseDetails__caseNo", flat=True).distinct()
            caseDataFiles=files.filter(caseDetails__caseNo__isnull=True)
            return Response({
                "folders":[
                {"name": s, "type": "folder", "level": "caseNo"}
                for s in caseData if s is not None
            ],
            "files":[
                {
                    "file_id": f.fileId,
                    "name": f.fileName,
                    "path":  request.build_absolute_uri(f.filePath) if f.filePath else None,
                    "created_at": f.created_at,
                    "uploaded_by": f.uploaded_by.first_name + ' ' + f.uploaded_by.last_name if f.uploaded_by else None
                }
                for f in caseDataFiles
            ]
            })
        elif division_id and year and caseNo and not caseType:
            # Return caseno as folders
            raw_ids = files.values_list("caseType", flat=True).distinct()
            print("files",files)
            case_type_ids = [int(i) for i in raw_ids if i and str(i).isdigit()]
            case_types = GeneralLookUp.objects.filter(lookupId__in=case_type_ids).values("lookupId", "lookupName")
            caseTypeFiles=files.filter(caseType__isnull=True)
            return Response({
                "folders":[
                {"id": s["lookupId"],"name": s["lookupName"],"type": "folder","level": "caseType"}
                for s in case_types if s is not None
            ],
            "files":[
                {
                    "file_id": f.fileId,
                    "name": f.fileName,
                    "path":  request.build_absolute_uri(f.filePath) if f.filePath else None,
                    "created_at": f.created_at,
                    "uploaded_by": f.uploaded_by.first_name + ' ' + f.uploaded_by.last_name if f.uploaded_by else None
                }
                for f in caseTypeFiles
            ]
            })
        elif division_id and year and caseNo and caseType and not fileTypeId:
            # Return file types as folders
            filetypes = files.values("fileType_id", "fileType__lookupName").distinct()
            fileTypeFiles=files.filter(fileType_id__isnull=True)
            return Response({
                "folders":[
                {
                    "id": ft["fileType_id"],
                    "name": ft["fileType__lookupName"],
                    "type": "folder",
                    "level": "filetype"
                }
                for ft in filetypes if ft["fileType_id"] is not None
            ],
            "files":[
                {
                    "file_id": f.fileId,
                    "name": f.fileName,
                    "path":  request.build_absolute_uri(f.filePath) if f.filePath else None,
                    "created_at": f.created_at,
                    "uploaded_by": f.uploaded_by.first_name + ' ' + f.uploaded_by.last_name if f.uploaded_by else None
                }
                for f in fileTypeFiles
            ]
            })
        elif division_id and year and caseNo and caseType and fileTypeId and not docTypeId:
            # Return file types as folders
            doctypes = files.values("documentType_id", "documentType__lookupName").distinct()
            docTypeFiles=files.filter(documentType_id__isnull=True)
            return Response({
                "folders":[
                {
                    "id": ft["documentType_id"],
                    "name": ft["documentType__lookupName"],
                    "type": "folder",
                    "level": "documenttype"
                }
                for ft in doctypes if ft["documentType_id"] is not None
            ],
            "files":[
                {
                    "file_id": f.fileId,
                    "name": f.fileName,
                    "path":  request.build_absolute_uri(f.filePath) if f.filePath else None,
                    "created_at": f.created_at,
                    "uploaded_by": f.uploaded_by.first_name + ' ' + f.uploaded_by.last_name if f.uploaded_by else None
                }
                for f in docTypeFiles
            ]
            })
        else:
            return Response([
                {
                    "name": f.fileName,
                    "file_id": f.fileId,
                    "path": request.build_absolute_uri(f.filePath) if f.filePath else None,
                    "created_at": f.created_at,
                    "uploaded_by": f.uploaded_by.first_name+' '+f.uploaded_by.last_name if f.uploaded_by else None
                }
                for f in files
            ])
        
class MoveFilesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        deptId = request.data.get("deptId")
        divsionId=request.data.get("divisionId")
        file_ids = request.data.get("file_ids")
        target_year = request.data.get("year")  # optional
        target_unitId = request.data.get("unitId")
        target_caseNo= request.data.get("caseNo")  
        target_caseType= request.data.get("caseType")  # optional
        target_filetype_id = request.data.get("file_type_id")  # optional
        target_documenttype_id = request.data.get("document_type_id")

        # if not file_id:
        #     return Response({"detail": "file_id is required."}, status=400)

        if isinstance(file_ids, (str, int)):
            file_ids = [file_ids]
        if not file_ids:
            return Response({"detail": "file_ids is required and must be a list."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if not target_caseNo:
            return Response({"detail":"Destination Case No is required"},status=status.HTTP_400_BAD_REQUEST)
        
        results = {"moved": [], "errors": []}
        for file_id in file_ids:
            try:
                file = FileDetails.objects.select_related("caseDetails").get(fileId=file_id)
                current_case = file.caseDetails

                if target_year:
                    current_case.year= target_year
                
                if target_unitId:
                    current_case.unitId= target_unitId

                # Update caseDetails if caseNo changes
                if target_caseNo and target_caseNo != current_case.caseNo:
                    new_case = CaseInfoDetails.objects.get(caseNo=target_caseNo)
                    file.caseDetails = new_case
                    current_case = new_case  # for further path building
                    file.caseType=None
                    file.fileType=None
                    file.documentType=None

                # Update caseType
                if target_caseType:
                    file.caseType = target_caseType
                    file.fileType = None
                    file.documentType = None

                if target_filetype_id:
                    file.fileType = GeneralLookUp.objects.get(lookupId=target_filetype_id)
                    file.documentType=None
            
                if target_documenttype_id:
                    file.documentType = GeneralLookUp.objects.get(lookupId=target_documenttype_id)
            
                current_case.save()

                # Build new file path
                relative_parts = []
                if deptId:
                    dept_name = Department.objects.get(departmentId=deptId).departmentName
                    relative_parts.append(str(dept_name))

                if file.division_id:
                    division_name = Division.objects.get(divisionId=file.division_id).divisionName
                    relative_parts.append(str(division_name))
            
                if target_year or current_case.year:
                    relative_parts.append(str(target_year or current_case.year))

                if target_unitId or current_case.unitId:
                    relative_parts.append(str(target_unitId or current_case.unitId))

                if target_caseNo or current_case.caseNo:
                    relative_parts.append(str(target_caseNo or current_case.caseNo))

                if target_caseType:
                    case_type = GeneralLookUp.objects.get(lookupId=target_caseType).lookupName
                    relative_parts.append(str(case_type))

                if target_filetype_id:
                    fileType= GeneralLookUp.objects.get(lookupId= target_filetype_id).lookupName
                    relative_parts.append(str(fileType))
            
                if target_documenttype_id:
                    documentType = GeneralLookUp.objects.get(lookupId=target_documenttype_id).lookupName
                    relative_parts.append(str(documentType))

                filename = os.path.basename(file.filePath)

                relative_parts.append(filename)

                new_relative_path = os.path.join("uploads","CID",*relative_parts)
                old_path = os.path.join(settings.MEDIA_ROOT,file.filePath)
                new_full_path = os.path.join(settings.MEDIA_ROOT, new_relative_path)

                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                os.rename(old_path, new_full_path)

                file.filePath = new_relative_path
                file.save()

                results["moved"].append(
                        {"fileId": file_id, "new_path": file.filePath})
                
            except FileDetails.DoesNotExist:
                results["errors"].append({"fileId": file_id, "reason": "File not found"})
            except CaseInfoDetails.DoesNotExist:
                results["errors"].append({"fileId": file_id, "reason": "Target Case not found"})
            except GeneralLookUp.DoesNotExist as e:
                results["errors"].append({"fileId":file_id,"detail": f"Invalid lookup reference: {str(e)}"})
            except Department.DoesNotExist:
                results["errors"].append({"fileId":file_id,"detail": "Invalid department."})
            except Division.DoesNotExist:
                results["errors"].append({"fileId":file_id,"detail": "Invalid division."})
            except Exception as e:
                results["errors"].append({"fileId":file_id, "reason": str(e)})

        if results["errors"]:
                return Response(results,status=status.HTTP_207_MULTI_STATUS)
                
        return Response(results,status=status.HTTP_200_OK)
            
            

class ArchiveFileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_id = request.data.get("file_id")

        if file_id is None:
            return Response(
                {"detail": "file_id is required and must be a list."},
                status=400,
            )
        
        if isinstance(file_id, int):
            file_id = [file_id]

        if not isinstance(file_id, (list, tuple)) or not file_id:
            return Response(
                {"detail": "file_id must be a non‑empty list of integers."}, status=400
            )
        try:
            file_id = list({int(fid) for fid in file_id})
        except (TypeError, ValueError):
            return Response({"detail": "require integers in array."}, status=400)
        files = FileDetails.objects.filter(fileId__in=file_id)
        found = {f.fileId: f for f in files}
        results = {fid: "not_found" for fid in file_id}

        for fid, file in found.items():
            if file.isArchieved:
                results[fid] = "already_archived"
                continue    
            old_path = file.filePath  # absolute path

            if not os.path.exists(old_path):
                results[fid] = "original file is missing"
                continue

            # Build new archive path: archive/<existing-relative-path>
            archive_relative_path = os.path.join("archive", file.filePath)
            new_path = os.path.join(settings.MEDIA_ROOT, archive_relative_path)

            # Ensure archive folder exists
            os.makedirs(os.path.dirname(new_path), exist_ok=True)

            try:
                os.rename(old_path, new_path)
                file.filePath = archive_relative_path
                file.isArchieved = True
                file.save(update_fields=("filePath", "isArchieved"))
                results[fid] = "archived"
            except OSError as e:
                results[fid] = f"error: {e!s}"

        return Response({"results": results},status=status.HTTP_200_OK)

       

class CopyFilesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_ids         = request.data.get("file_ids", [])         # list of file IDs to copy
        division_id      = request.data.get("divisionId")
        year             = request.data.get("year")
        case_no       = request.data.get("caseNo")
        case_type     = request.data.get("caseType")
        file_type_id     = request.data.get("fileTypeId")
        document_type_id = request.data.get("documentTypeId")

        if not (division_id and year and case_no):
            return Response({"error": "divisionId, year, and caseNo are required."}, status=400)

        copied_files = []

        for fid in file_ids:
            try:
                original_file = FileDetails.objects.get(fileId=fid)

                # Fetch or create the correct caseInfoDetails entry
                case_obj, _ = CaseInfoDetails.objects.get_or_create(division_id=division_id,year=year,caseNo=case_no)

                parts = [str(division_id), str(year), str(case_no)]
                if case_type:
                    parts.append(str(case_type))
                if file_type_id:
                    parts.append(str(file_type_id))
                if document_type_id:
                    parts.append(str(document_type_id))

                original_filename = os.path.basename(original_file.filePath)
                new_filename = f"{uuid4()}_{original_filename}"
                new_path = "/".join(parts + [new_filename])
                    
                if original_file.filePath and default_storage.exists(original_file.filePath):
                    with default_storage.open(original_file.filePath, 'rb') as src:
                        saved_path = default_storage.save(new_path, src)
                else:
                    saved_path = None

                # Create new FileDetails entry
                new_file = FileDetails.objects.create(
                    caseDetails=case_obj,
                    division_id=division_id,
                    caseType=case_type,
                    fileType_id=file_type_id,
                    documentType_id=document_type_id,
                    fileName=original_file.fileName,
                    filePath=saved_path,
                    fileHash=original_file.fileHash,
                    uploaded_by=request.user,
                    classification= original_file.classification,
                    is_approved=original_file.is_approved
                )

                copied_files.append({
                    "original_file_id": fid,
                    "new_file_id": new_file.fileId,
                    "path": request.build_absolute_uri(new_file.filePath) if new_file.filePath else None
                })

            except FileDetails.DoesNotExist:
                continue

        return Response({"copied": copied_files}, status=status.HTTP_200_OK)       

class ArchiveFullTreeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        division_id = request.query_params.get("division_id")
        if not division_id:
            return Response(
                {"detail": "division_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            division_id = int(division_id)
        except ValueError:
            return Response(
                {"detail": "division_id must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        dept_ids, div_ids = user_access_scope(user)

        if division_id not in div_ids:
            return Response(
                {"detail": "You are not authorised for this division."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        files = FileDetails.objects.select_related(
                "division",
                "division__departmentId",
                "caseDetails",
                "fileType",
                "documentType"
            ).filter(
                division_id=division_id,isArchieved=True
            )
        if not files.exists():
            return Response([], status=status.HTTP_200_OK)
        tree = nested_dict()

        for f in files:
            dept = f.division.departmentId
            div = f.division
            case = f.caseDetails
            year    = case.year
            unitId = case.unitId
            case_no = case.caseNo
            case_type = GeneralLookUp.objects.get(lookupId= f.caseType)
            file_type = f.fileType
            doc_type = f.documentType

            node = tree[dept.pk]
            node["_meta"] = {"id": dept.pk, "name": dept.departmentName, "level": "department", "type": "folder"}

            node = node[div.pk]
            node["_meta"] = {"id": div.pk, "name": div.divisionName, "level": "division", "type": "folder"}

            node = node[year]
            node["_meta"] = {"name": str(year), "level": "year","type": "folder"}

            node = node[unitId]
            node["_meta"] = {"id":str(unitId),"name": UnitMaster.objects.get(unitId=unitId).unitName, "level": "unitId","type": "folder"}

            node = node[case_no]
            node["_meta"] = {"name": case_no, "level": "caseNo", "type": "folder"}

            node = node[case_type.lookupId if case_type else None]
            node["_meta"] = {
                "id": case_type.lookupId if case_type else None,
                "name": case_type.lookupName if case_type else None,
                "level": "caseType",
                "type": "folder"
            }

            node = node[file_type.lookupId if file_type else None]
            node["_meta"] = {
                "id": file_type.lookupId if file_type else None,
                "name": file_type.lookupName if file_type else None,
                "level": "filetype",
                "type": "folder"
            }

            node = node[doc_type.lookupId if doc_type else None]
            node["_meta"] = {
                "id": doc_type.lookupId if doc_type else None,
                "name": doc_type.lookupName if doc_type else None,
                "level": "documenttype",
                "type": "folder"
            }

            node.setdefault("files", []).append({
                "file_id": f.fileId,
                "name": f.fileName,
                "path": request.build_absolute_uri(f.filePath) if f.filePath else None,
                "created_at": f.created_at,
                "uploaded_by": f.uploaded_by.first_name if f.uploaded_by else None
            })

        # Convert nested dict to JSON serializable structure
        def dictify(node_dict):
            meta = node_dict.pop("_meta", {})
            children = [dictify(child) for child in node_dict.values() if isinstance(child, dict)]
            if children:
                meta["children"] = sorted(children, key=lambda x: str(x.get("name")))
            if "files" in node_dict:
                meta["files"] = node_dict["files"]
            return meta

        response = [dictify(v) for v in tree.values()]
        return Response(sorted(response, key=lambda x: x.get("name")), status=status.HTTP_200_OK)  
    
class UnArchiveFileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_id = request.data.get("file_id")

        if file_id is None:
            return Response({"detail": "file_id  is required."}, status=400)
        
        if isinstance(file_id, int):
            file_id = [file_id]

        if not isinstance(file_id, (list, tuple)) or not file_id:
            return Response({"detail": "Must be a non-empty list of integers."}, status=400)

        try:
            file_id = list({int(fid) for fid in file_id})
        except (TypeError, ValueError):
            return Response({"detail": "All IDs must be integers."}, status=400)

        files_qs = FileDetails.objects.filter(fileId__in=file_id)
        found = {f.fileId: f for f in files_qs}
        results = {fid: "not_found" for fid in file_id}

        for fid, file in found.items():
            if not file.isArchieved:
                results[fid] = "not_archived"
                continue

            archived_path = file.filePath  # e.g., "archive/..."
            if not re.match(r"^archive[\\/]", archived_path):
                results[fid] = "invalid_archive_path"
                continue

            archived_full_path = os.path.join(settings.MEDIA_ROOT, archived_path)

            # Remove "archive/" prefix to get original relative path
            original_relative_path = re.sub(r"^archive[\\/]", "", archived_path)
            original_full_path = os.path.join(settings.MEDIA_ROOT, original_relative_path)

            if not os.path.exists(archived_full_path):
                results[fid] = "archived_file_missing"
                continue

            try:
                os.makedirs(os.path.dirname(original_full_path), exist_ok=True)
                os.rename(archived_full_path, original_full_path)

                file.filePath = original_relative_path
                file.isArchieved = False
                file.save(update_fields=("filePath", "isArchieved"))

                results[fid] = "unarchived"
            except OSError as e:
                results[fid] = f"error: {str(e)}"

        return Response({"results": results}, status=status.HTTP_200_OK)

class FolderTreeFullAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def _nested_dict(self):
        return defaultdict(self._nested_dict)
    
    def _lookup_name(self, lookup_id, cache):
        if not lookup_id:
            return None
        if lookup_id in cache:
            return cache[lookup_id]
        name = (
            GeneralLookUp.objects.filter(lookupId=lookup_id)
            .values_list("lookupName", flat=True)
            .first()
        )
        cache[lookup_id] = name
        return name

    def post(self, request):
        user          = request.user
        division_id   = request.data.get("division_id")
        year          = request.data.get("year")
        unit_id       = request.data.get("unitId")
        case_no    = request.data.get("caseNo")
        case_type  = request.data.get("caseType")
        file_type_id  = request.data.get("fileTypeId")
        doc_type_id   = request.data.get("documentTypeId")

        user_designations = user.designation.all()

        user_division_ids = Division.objects.filter(
            designation__in=user_designations
        ).values_list("divisionId", flat=True)

        user_department_ids = Department.objects.filter(
            designation__in=user_designations
        ).values_list("departmentId", flat=True)

        if division_id and int(division_id) not in user_division_ids:
            return Response({"detail": "Unauthorized for this division"}, status=403)
        
        files = FileDetails.objects.select_related(
            "division",
            "caseDetails",
            "fileType",
            "documentType",
            "division__departmentId",
        ).filter(
            Q(division_id__in=user_division_ids) | Q(division__departmentId__in=user_department_ids),
            isArchieved=False,)
        
        if division_id:
            files = files.filter(division_id=division_id)
        if year:
            files = files.filter(caseDetails__year=int(year))
        if unit_id:
            files = files.filter(caseDetails__unitId=int(unit_id))
        if case_no:
            files = files.filter(caseDetails__caseNo=str(case_no))
        if case_type:
            files = files.filter(caseType=case_type)
        if file_type_id:
            files = files.filter(fileType_id=file_type_id)
        if doc_type_id:
            files = files.filter(documentType_id=doc_type_id)
        
        tree = self._nested_dict()
        lookup_cache = {}

        for f in files:
            division = f.division
            case  = f.caseDetails

            div_id   = f.division.divisionId
            div_name = f.division.divisionName

            node = tree[div_id]
            node.setdefault("_meta", {
                "id": div_id,
                "name": div_name,
                "level": "division",
                "type": "folder"
            })

            levels = []

            if case.year:
                levels.append(("year", case.year, str(case.year)))

            if case.unitId:
                name = UnitMaster.objects.get(unitId = case.unitId)
                levels.append(("unitId", str(case.unitId),name.unitName))

            if case.caseNo:
                levels.append(("caseNo", case.caseNo, str(case.caseNo)))

            if f.caseType:
                name = self._lookup_name(f.caseType, lookup_cache)
                if name:
                    levels.append(("caseType", f.caseType, name))

            if f.fileType_id:
                name = self._lookup_name(f.fileType_id, lookup_cache)
                if name:
                    levels.append(("fileType", f.fileType_id, name))

            if f.documentType_id:
                name = self._lookup_name(f.documentType_id, lookup_cache)
                if name:
                    levels.append(("documentType", f.documentType_id, name))

            # Traverse into nested tree
            for level_key, level_id, level_name in levels:
                node = node[level_id]
                if "_meta" not in node:
                    node["_meta"] = {
                        "id": level_id,
                        "name": level_name,
                        "level": level_key,
                        "type": "folder"
                    }

            node.setdefault("files", []).append({
                "file_id": f.fileId,
                "name": f.fileName,
                "path": request.build_absolute_uri(f.filePath) if f.filePath else None,
                "created_at": f.created_at,
                "uploaded_by": f"{f.uploaded_by.first_name} {f.uploaded_by.last_name}" if f.uploaded_by else None
            })

        # ───── Convert tree ─────
        def dictify(node):
            meta = node.pop("_meta")
            children = []

            for key, child in node.items():
                if key == "files":
                    meta["files"] = child
                else:
                    children.append(dictify(child))

            if children:
                children.sort(key=lambda c: str(c["name"]))
                meta["children"] = children
            return meta

        result = [dictify(child) for child in tree.values()]
        result.sort(key=lambda c: str(c["name"]))

        return Response(result, status=status.HTTP_200_OK)
    
class MergecaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _target_prefix(self, dst_case_no, dst_case):
        example_file = FileDetails.objects.filter(caseDetails=dst_case).first()
        if not example_file or not example_file.filePath:
            return None
        parts = Path(example_file.filePath.replace("\\", "/")).parts
        try:
            idx = parts.index(str(dst_case_no))
            return parts[: idx + 1]  # include dst_case_no
        except ValueError:
            return None
            


    def post(self, request):
        src_no = str(request.data.get("sourceCaseNo") or "").strip()
        dst_no = str(request.data.get("destinationCaseNo") or "").strip()

        if not src_no or not dst_no:
            return Response({"detail": "Both source and destination case numbers are required."}, status=400)
        if src_no == dst_no:
            return Response({"detail": "Source and destination case numbers must differ."}, status=400)

        # Fetch case details
        try:
            src_case = CaseInfoDetails.objects.get(caseNo=src_no)
        except CaseInfoDetails.DoesNotExist:
            return Response({"detail": f"Source case '{src_no}' not found."}, status=404)
        try:
            dst_case = CaseInfoDetails.objects.get(caseNo=dst_no)
        except CaseInfoDetails.DoesNotExist:
            return Response({"detail": f"Destination case '{dst_no}' not found."}, status=404)

        # Fetch file list
        files = FileDetails.objects.filter(caseDetails=src_case)
        if not files.exists():
            return Response({"detail": "No files to merge from source case."}, status=404)

        moved, skipped, renamed, errors = 0, 0, [], []

        dst_prefix_parts = self._target_prefix(dst_no, dst_case)

        with transaction.atomic():
            for f in files:
                old_rel = f.filePath.replace("\\", "/")
                if not old_rel:
                    skipped += 1
                    errors.append(f"Missing path for file ID {f.fileId}")
                    continue

                old_abs = os.path.join(settings.MEDIA_ROOT, old_rel)
                if not os.path.exists(old_abs):
                    skipped += 1
                    errors.append(f"File not found on disk: {old_rel}")
                    continue

                parts = Path(old_rel).parts
                try:
                    src_idx = parts.index(str(src_no))
                except ValueError:
                    skipped += 1
                    errors.append(f"'{src_no}' not found in path: {old_rel}")
                    continue

                tail_parts = parts[src_idx + 1:]

                if dst_prefix_parts:
                    new_parts = list(dst_prefix_parts) + list(tail_parts)
                else:
                    # fallback if no dst files yet
                    new_parts = list(parts[:src_idx]) + [dst_no] + list(tail_parts)

                new_rel = "/".join(new_parts)
                new_abs = os.path.join(settings.MEDIA_ROOT, new_rel)

                os.makedirs(os.path.dirname(new_abs), exist_ok=True)

                # Rename if exists
                if os.path.exists(new_abs):
                    base, ext = os.path.splitext(new_abs)
                    count = 1
                    while os.path.exists(f"{base}_{count}{ext}"):
                        count += 1
                    new_abs = f"{base}_{count}{ext}"
                    new_rel = os.path.relpath(new_abs, settings.MEDIA_ROOT)
                    renamed.append({
                        "original": os.path.basename(old_rel),
                        "new": os.path.basename(new_abs),
                        "path": new_rel.replace("\\", "/")
                    })

                try:
                    os.rename(old_abs, new_abs)
                except OSError as e:
                    skipped += 1
                    errors.append(f"Rename error for file {f.fileId}: {str(e)}")
                    continue

                # Update DB
                f.filePath = new_rel.replace("\\", "/")
                f.caseDetails = dst_case
                f.save(update_fields=["filePath", "caseDetails"])
                moved += 1

            # Clean up empty folders from source
            src_root = os.path.join(settings.MEDIA_ROOT)
            for root, dirs, files in os.walk(src_root, topdown=False):
                if src_no in root and not files and not dirs:
                    try:
                        os.rmdir(root)
                    except Exception:
                        pass

        response = {
            "detail": "Merge completed with warnings." if errors else "Merge completed successfully.",
            "files_moved": moved,
            "files_skipped": skipped,
            "renamed": renamed,
            "errors": errors,
        }
        return Response(response, status=400 if errors else 200)
    


    
