from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FileDetails, FileAccessRequest, Notification
from users.models import UserDivisionRole
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
        user_division_role = UserDivisionRole.objects.filter(user=uploader).first()

        if user_division_role:
            user_division = user_division_role.division
            # Notify only viewers (roleid = 4) content manager
            cm_users = UserDivisionRole.objects.filter(role__roleId=4, division=user_division)
            for cm in cm_users:
                _user = cm.user
                Notification.objects.create(
                    recipient=_user,
                    message=(
                        f"Files has been uploaded for case no: "
                        f"{instance.caseDetails.caseNo} by {instance.uploaded_by}"
                    ),
                    file=instance,
                    division = user_division
                )
