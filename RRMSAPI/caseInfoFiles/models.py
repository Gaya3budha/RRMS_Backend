from django.db import models
from users.models import User


# Create your models here.

class CaseInfoDetails(models.Model):
    CaseInfoDetailsId = models.AutoField(primary_key = True)
    stateId = models.IntegerField()
    districtId = models.IntegerField()
    unitId = models.IntegerField()
    Office = models.TextField(max_length=255)
    letterNo = models.CharField(max_length=100)
    caseDate = models.DateTimeField()
    caseType = models.CharField(max_length = 100)
    caseNo = models.CharField(max_length=100)
    firNo = models.CharField(max_length=255)
    author = models.TextField(max_length = 200)
    toAddr = models.TextField(max_length = 500)
    lastmodified_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True,blank = True)
    lastmodified_Date = models.DateTimeField(auto_now_add=True, null = True,blank = True)

    class Meta:
        permissions = [
            ("view_searchcaseFiles","can search the case and file details"),
            ("add_filepreviewapi","can preview a file"),
        ]
    def __str__(self):
        return self.caseNo

class FileDetails(models.Model):
    CLASSIFICATION_CHOICES = [
        ('public', 'Public'),
        ('confidential', 'Confidential'),
    ]

    fileId = models.AutoField(primary_key = True)
    caseDetails = models.ForeignKey('CaseInfoDetails',on_delete=models.CASCADE, related_name = 'files')
    fileName = models.CharField(max_length=255)
    filePath = models.TextField()
    fileHash = models.CharField(max_length=64)
    hashTag = models.TextField(null =True, blank = True)
    subject = models.TextField(max_length = 1000, null =True, blank = True)
    fileType = models.TextField(max_length = 100,null =True, blank = True)
    classification = models.TextField(max_length = 20, choices=CLASSIFICATION_CHOICES)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True,blank = True)
    created_at = models.DateTimeField(auto_now_add=True, null = True,blank = True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.fileName

class FavouriteFiles(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name = 'favorited_by')
    file = models.ForeignKey('FileDetails',on_delete=models.CASCADE, related_name = 'favourites')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'file')


class FileUsage(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    file = models.ForeignKey('FileDetails',on_delete=models.CASCADE)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'file')


class FileAccessPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(FileDetails, on_delete=models.CASCADE, related_name='access_permissions')
    can_view = models.BooleanField(default=True)

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    file = models.ForeignKey(FileDetails, on_delete=models.CASCADE, null=True, blank=True) 