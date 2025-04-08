from django.db import models


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
    subject  = models.TextField(max_length = 1000)
    caseNo = models.CharField(max_length=100)
    firNo = models.CharField(max_length=255)
    author = models.TextField(max_length = 200)
    toAddr = models.TextField(max_length = 500)

    class Meta:
        permissions = [
            ("can_search_caseFiles","can search the case and file details"),
        ]
    def __str__(self):
        return self.caseNo

class FileDetails(models.Model):
    fileId = models.AutoField(primary_key = True)
    caseDetails = models.ForeignKey('CaseInfoDetails',on_delete=models.CASCADE, related_name = 'files')
    fileName = models.CharField(max_length=255)
    filePath = models.TextField()
    fileHash = models.CharField(max_length=64)
    hashTag = models.TextField(null =True, blank = True)
    subject = models.TextField(max_length = 1000, null =True, blank = True)
    fileType = models.TextField(max_length = 100,null =True, blank = True)
    classification = models.TextField(max_length = 200, default="private")


    def __str__(self):
        return self.fileName

