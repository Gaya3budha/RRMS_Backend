from django.db import models
from users.models import User
from mdm.models import CaseStatus, FileClassification, FileType, DivisionMaster, GeneralLookUp
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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
    caseNo = models.CharField(max_length=17, unique=True)
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
    fileType = models.ForeignKey(GeneralLookUp,on_delete=models.CASCADE, null = True,blank = True,related_name="file_type")
    classification = models.ForeignKey(GeneralLookUp,on_delete=models.CASCADE,null = True,blank = True,related_name="file_classification")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True,blank = True)
    created_at = models.DateTimeField(auto_now_add=True, null = True,blank = True)
    is_approved = models.BooleanField(default=False)
    division= models.ForeignKey(DivisionMaster, null= True, blank=True,on_delete=models.CASCADE)
    documentType = models.ForeignKey(GeneralLookUp,on_delete=models.CASCADE,null= True, blank= True,related_name="document_type")
    comments = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return self.fileName

class FileUploadApproval(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('revoked', 'Revoked'),
        ('denied', 'Denied'),
    ]
    file = models.ForeignKey(FileDetails, on_delete=models.CASCADE)
    case_details_id= models.ForeignKey(CaseInfoDetails,on_delete=models.CASCADE,null=True,blank=True)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='upload_approver')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    department = models.IntegerField(null=True, blank=True)
    division = models.ForeignKey(DivisionMaster, null=True,blank=True,on_delete=models.CASCADE)
    department = models.IntegerField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    comments = models.TextField(null= True, blank = True)


class FileAccessRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('revoked', 'Revoked'),
        ('denied', 'Denied'),
    ]
    file = models.ForeignKey(FileDetails, on_delete=models.CASCADE)
    case_details_id= models.ForeignKey(CaseInfoDetails,on_delete=models.CASCADE,null=True,blank=True)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="access_requests")
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_requests")
    requested_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="file_requests_received",null = True, blank = True)
    comments = models.TextField(null= True, blank = True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null = True, blank =True)
    division = models.ForeignKey(DivisionMaster, null=True,blank=True,on_delete=models.CASCADE)
    department = models.IntegerField(null=True, blank=True)
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
    NOTIFICATION_TYPES = [
        ("UPLOAD_APPROVAL", "Upload Approval"),
        ("ACCESS_REQUEST", "Access Request"),
        ("GENERIC", "Generic"),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    division = models.ForeignKey(DivisionMaster,null = True, blank=True, on_delete=models.CASCADE)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default="GENERIC")
    department = models.IntegerField(null= True,blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    # file = models.ForeignKey(FileDetails, on_delete=models.CASCADE, null=True, blank=True)
    requestedBy = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name="requested_by")
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    reference_object = GenericForeignKey('content_type', 'object_id')
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()