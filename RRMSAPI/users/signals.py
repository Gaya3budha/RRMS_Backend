from django.dispatch import receiver
from caseInfoFiles.models import Notification
from users.models import PasswordResetRequest, User
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType

@receiver(post_save, sender=PasswordResetRequest)
def notify_admin_on_pwd_reset_request(sender, instance, created, **kwargs):
    if created:
        message = (f"Password reset request received for kgid: {instance.kgid}"
          f"Name: {instance.first_name} {instance.last_name}, "
            f"Email: {instance.email}, Mobile: {instance.mobileno}."
        )

        content_type = ContentType.objects.get_for_model(instance)

        admins = User.objects.filter(is_staff=True, is_active=True)

        for admin in admins:
            Notification.objects.create(
                 recipient=admin,
                message=message,
                type="GENERIC", 
                department=None,  
                division=None,   
                requestedBy=instance.requested_by,  
                content_type=content_type,
                object_id=instance.passwordResetRequestId
            )