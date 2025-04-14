from .models import FileUsage
from django.utils import timezone

def record_file_access(user, file):
    FileUsage.objects.update_or_create(
        user=user,
        file=file,
        defaults={'last_accessed': timezone.now()}
    )