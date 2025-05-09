from django.db import models
from users.models import User
from mdm.models import CaseStatus, FileClassification, FileType, DivisionMaster

# Create your models here.

class CaseInfoDetails(models.Model):
    CaseInfoDetailsId = models.AutoField(primary_key = True)
    stateId = models.IntegerField()
    districtId = models.IntegerField()
    unitId = models.IntegerField()
    Office = models.TextField(max_length=255)
    letterNo = models.CharField(max_length=100)
    caseDate = models.DateTimeField(null=True,blank=True)
    caseType = models.CharField(max_length = 100)
    caseNo = models.CharField(max_length=100)
    firNo = models.CharField(max_length=255)
    author = models.TextField(max_length = 200)
    toAddr = models.TextField(max_length = 500)
    year = models.IntegerField(null = True,blank = True)
    caseStatus = models.IntegerField( null = True, blank= True)
    lastmodified_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True,blank = True)
    lastmodified_Date = models.DateTimeField(auto_now_add=True, null = True,blank = True)
    division  = models.ForeignKey(DivisionMaster,blank= True, null=True,on_delete=models.CASCADE) 

    class Meta:
        permissions = [
            ("view_searchcaseFiles","can search the case and file details"),
            ("add_filepreviewapi","can preview a file"),
        ]
    def __str__(self):
        return self.caseNo

class FileDetails(models.Model):
    FILE_STAGE_CHOICES = [
        ('Enquiry', 'enquiry'),
        ('I/O', 'i/o'),
        ('Crime', 'crime')
    ]
    fileId = models.AutoField(primary_key = True)
    caseDetails = models.ForeignKey('CaseInfoDetails',on_delete=models.CASCADE, related_name = 'files')
    fileName = models.CharField(max_length=255)
    filePath = models.TextField()
    fileHash = models.CharField(max_length=64)
    hashTag = models.TextField(null =True, blank = True)
    subject = models.TextField(max_length = 1000, null =True, blank = True)
    fileType = models.IntegerField( null = True,blank = True)
    classification = models.IntegerField(null = True,blank = True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True,blank = True)
    created_at = models.DateTimeField(auto_now_add=True, null = True,blank = True)
    is_approved = models.BooleanField(default=False)
    division= models.ForeignKey(DivisionMaster, null= True, blank=True,on_delete=models.CASCADE)
    filestage = models.CharField(max_length=20, choices=FILE_STAGE_CHOICES, null= True, blank= True)
    comments = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return self.fileName

class FileAccessRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('revoked', 'Revoked'),  # Add this
        ('denied', 'Denied'),
    ]
    file = models.ForeignKey(FileDetails, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="access_requests")
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_requests")
    requested_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="file_requests_received",null = True, blank = True)
    comments = models.TextField(null= True, blank = True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null = True, blank =True)
    division = models.ForeignKey(DivisionMaster, null=True,blank=True,on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class FavouriteFiles(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name = 'favorited_by')
    file = models.ForeignKey('FileDetails',on_delete=models.CASCADE, related_name = 'favourites')
    added_at = models.DateTimeField(auto_now_add=True)
    division = models.ForeignKey(DivisionMaster,null=True,blank=True,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'file')


class FileUsage(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    file = models.ForeignKey('FileDetails',on_delete=models.CASCADE)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'file')


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    division = models.ForeignKey(DivisionMaster,null = True, blank=True, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    file = models.ForeignKey(FileDetails, on_delete=models.CASCADE, null=True, blank=True) 

