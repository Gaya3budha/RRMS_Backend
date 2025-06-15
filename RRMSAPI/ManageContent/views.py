import os
from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework import status
from collections import defaultdict

from caseInfoFiles.models import CaseInfoDetails, FileDetails
from mdm.models import Department, Division, GeneralLookUp
from users.models import User

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
        # file_id = request.data.get("file_id")
        file_ids = request.data.get("file_ids")
        target_year = request.data.get("year")  # optional
        target_caseNo= request.data.get("caseNo")  # optional
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
        
        results = {"moved": [], "errors": []}
        for file_id in file_ids:
            try:
                file = FileDetails.objects.select_related("caseDetails").get(fileId=file_id)
                current_case = file.caseDetails

                if target_year:
                    current_case.year= target_year

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

class ArchiveFileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_id = request.data.get("file_id")

        if not file_id:
            return Response({"detail": "file_id is required."}, status=400)

        try:
            file = FileDetails.objects.get(fileId=file_id)
            old_path = file.filePath  # absolute path

            # Build new archive path: archive/<existing-relative-path>
            archive_relative_path = os.path.join("archive", file.filePath)
            new_path = os.path.join(settings.MEDIA_ROOT, archive_relative_path)

            # Ensure archive folder exists
            os.makedirs(os.path.dirname(new_path), exist_ok=True)

            if not os.path.exists(old_path):
                return Response({"detail": "Original file not found."}, status=404)

            os.rename(old_path, new_path)

            # Update filePath and mark as archived
            file.filePath = archive_relative_path
            file.isArchieved = True
            file.save()

            return Response({"detail": "File archived successfully."}, status=200)

        except FileDetails.DoesNotExist:
            return Response({"detail": "File not found."}, status=404)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)
        

class FolderTreeFullAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user          = request.user
        division_id   = request.data.get("division_id")
        year          = request.data.get("year")
        case_no    = request.data.get("caseNo")
        case_type  = request.data.get("caseType")
        file_type_id  = request.data.get("fileTypeId")
        doc_type_id   = request.data.get("documentTypeId")

        user_designations = user.designation.all()

        user_division_ids = Division.objects.filter(
            designation__in=user_designations
        ).values_list("divisionId", flat=True).distinct()

        user_department_ids = Department.objects.filter(
            designation__in=user_designations
        ).values_list("departmentId", flat=True).distinct()

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
        if case_no:
            files = files.filter(caseDetails__caseNo=str(case_no))
        if case_type:
            files = files.filter(caseType=case_type)
        if file_type_id:
            files = files.filter(fileType_id=file_type_id)
        if doc_type_id:
            files = files.filter(documentType_id=doc_type_id)

        def nested_dict():
            return defaultdict(nested_dict)
        
        tree = nested_dict()
        for f in files:
            div_id   = f.division.divisionId
            div_name = f.division.divisionName

            yr   = f.caseDetails.year or "UNASSIGNED"
            sno  = f.caseDetails.caseNo or "UNASSIGNED"
            stp  = (f.caseType and int(f.caseType)) or "UNASSIGNED"
            ftp  = (f.fileType_id or "UNASSIGNED")
            dtp  = (f.documentType_id or "UNASSIGNED")

            leaf = tree[div_id]
            leaf.setdefault("_meta", {"id": div_id, "name": div_name, "level": "division", "type": "folder"})

            leaf = leaf[yr]
            leaf.setdefault("_meta", {"name": yr, "level": "year", "type": "folder"})

            leaf = leaf[sno]
            leaf.setdefault("_meta", {"name": sno, "level": "caseNo", "type": "folder"})

            leaf = leaf[stp]
            if stp != "UNASSIGNED":
                stp_name = GeneralLookUp.objects.filter(lookupId=stp).values_list("lookupName", flat=True).first()
            else:
                stp_name = "UNASSIGNED"
            leaf.setdefault("_meta", {"id": stp, "name": stp_name, "level": "caseType", "type": "folder"})

            leaf = leaf[ftp]
            if ftp != "UNASSIGNED":
                ftp_name = GeneralLookUp.objects.filter(lookupId=ftp).values_list("lookupName", flat=True).first()
            else:
                ftp_name = "UNASSIGNED"
            leaf.setdefault("_meta", {"id": ftp, "name": ftp_name, "level": "filetype", "type": "folder"})

            leaf = leaf[dtp]
            if dtp != "UNASSIGNED":
                dtp_name = GeneralLookUp.objects.filter(lookupId=dtp).values_list("lookupName", flat=True).first()
            else:
                dtp_name = "UNASSIGNED"
            leaf.setdefault("_meta", {"id": dtp, "name": dtp_name, "level": "documenttype", "type": "folder"})

            leaf.setdefault("files", []).append({
                "file_id":   f.fileId,
                "name":      f.fileName,
                "path":      request.build_absolute_uri(f.filePath) if f.filePath else None,
                "created_at": f.created_at,
                "uploaded_by": f"{f.uploaded_by.first_name} {f.uploaded_by.last_name}" if f.uploaded_by else None,
            })

        # ───────────────────────────────────────────────────────────
        # 3. Convert the defaultdict tree to plain lists / dicts
        # ───────────────────────────────────────────────────────────
        def dictify(node):
            """Recursively convert `_meta` + children to frontend JSON."""
            meta = node.pop("_meta")
            children = []
            for key, child in node.items():
                if key == "files":
                    # keep files list at this level
                    meta["files"] = child
                else:
                    children.append(dictify(child))
            if children:
                # Sort children folders alphabetically / numerically
                children.sort(key=lambda c: str(c["name"]))
                meta["children"] = children
            return meta

        full_tree = [dictify(child) for child in tree.values()]
        # Sort divisions alphabetically
        full_tree.sort(key=lambda c: str(c["name"]))

        return Response(full_tree, status=status.HTTP_200_OK)