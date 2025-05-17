from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FileDetails, FileAccessRequest, Notification, FileUploadApproval
from mdm.models import Designation
# from users.models import UserDivisionRole
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model


User = get_user_model()

@receiver(post_save, sender=FileAccessRequest)
def notify_on_access_request(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(FileAccessRequest)

        Notification.objects.create(
            recipient=instance.requested_to,
            message=f"{instance.requested_by} has requested access to file: {instance.file.fileName}",
            requestedBy=instance.requested_by,
            division=instance.division,
            type='ACCESS_REQUEST',
            content_type=content_type,
            object_id=instance.id,
        )

@receiver(post_save, sender=FileDetails)
def notify_admin_on_upload(sender, instance, created, **kwargs):
    if  created and not instance.is_approved:
        uploader = instance.uploaded_by

        # designation_id = instance.designation_id
        # print('designation',designation_id)
        division = instance.division
        print('division',division)

        department = division.departmentId 
        print('department',department)

        # designations =Designation.objects.filter(division= division.divisionId)

        # print('designations',designations)
        
        eligible_users = User.objects.filter(
            designation__division=division,
            role__roleId__in=[3]  # Admin (1) or Viewer (4) role
        ).exclude(id=uploader.id).distinct()

        print('eligible_users',eligible_users)
        
        notified_users= set()
        for user in eligible_users:
            upload_approval = FileUploadApproval.objects.create(
                    file=instance,
                    requested_by=uploader,
                    case_details_id = instance.caseDetails,
                    division = division,
                    reviewed_by = user
                )
            content_type = ContentType.objects.get_for_model(upload_approval)
            Notification.objects.create(
                    recipient=user,
                    requestedBy=uploader,
                    division=division,
                    message=(
                        f"Files has been uploaded for case no: "
                        f"{instance.caseDetails.caseNo} by {instance.uploaded_by}"
                    ),
                    type='UPLOAD_APPROVAL',
                    content_type=content_type,
                    object_id=upload_approval.id,
                )
            notified_users.add(user.id)
