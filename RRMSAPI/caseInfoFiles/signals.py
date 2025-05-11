from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FileDetails, FileAccessRequest, Notification, FileUploadApproval
# from users.models import UserDivisionRole
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model


User = get_user_model()

@receiver(post_save, sender=FileAccessRequest)
def notify_on_access_request(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.requested_to,
            message=f"{instance.requested_by} has requested access to file: {instance.file.fileName}",
            file=instance.file
        )

@receiver(post_save, sender=FileDetails)
def notify_admin_on_upload(sender, instance, created, **kwargs):
    if created and not instance.is_approved:
        uploader = instance.uploaded_by
        # user_division_role = UserDivisionRole.objects.filter(user=uploader).first()

        # if user_division_role:
        #     user_division = user_division_role.division
        #     print("instance.caseDetails- ",instance.caseDetails)
            
            # Notify only viewers (roleid = 4) 
            # cm_users = UserDivisionRole.objects.filter(role__roleId=4, division=user_division)
            # reviewers_and_admins = UserDivisionRole.objects.filter(
            #     role__roleId__in=[1, 4],  # admin + Content Manager
            #     division=user_division
            # )


            # notified_users= set()

            # for cm in reviewers_and_admins:
            #     _user = cm.user

            #     upload_approval = FileUploadApproval.objects.create(
            #         file=instance,
            #         requested_by=uploader,
            #         case_details_id = instance.caseDetails,
            #         division = user_division,
            #         reviewed_by = _user
            #     )
            #     content_type = ContentType.objects.get_for_model(upload_approval)
            #     Notification.objects.create(
            #         recipient=_user,
            #         message=(
            #             f"Files has been uploaded for case no: "
            #             f"{instance.caseDetails.caseNo} by {instance.uploaded_by}"
            #         ),
            #         # file=instance,
            #         division = user_division,
            #         type="UPLOAD_APPROVAL",
            #         content_type=content_type,
            #         object_id=upload_approval.id,
            #     )
            #     notified_users.add(_user.id)
