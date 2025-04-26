from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FileDetails, FileAccessRequest, Notification

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
        user_division = uploader.divisionmaster_id
        # Notify only viewers (roleid = 4) content manager
        cm_users = User.objects.filter(role_id=4, divisionmaster_id=user_division)
        for cm in cm_users:
            Notification.objects.create(
                recipient=cm,
                message=(
                    f"A new file has been uploaded for case no: "
                    f"{instance.caseDetails.caseNo} by {instance.uploaded_by}"
                ),
                file=instance 
            )
