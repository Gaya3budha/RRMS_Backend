from .models import FileAccessPermission,FileDetails
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

@receiver(post_save, sender=FileDetails)
def assign_permission_on_private_file(sender, instance, created, **kwargs):
    if created and instance.classification == 'private':
        FileAccessPermission.objects.create(user=instance.CaseInfoDetails.user, file=instance)

@receiver(post_save, sender=FileDetails)
def notify_admin_on_upload(sender, instance, created, **kwargs):
    if created and not instance.is_approved:
        # Notify only viewers (roleid = 4) content manager
        cm_users = User.objects.filter(roleid=4)
        for cm in cm_users:
            Notification.objects.create(
                recipient=cm,
                message=(
                    f"A new file has been uploaded for case no: "
                    f"{instance.caseDetails.caseNo} by {instance.uploaded_by}"
                )
            )