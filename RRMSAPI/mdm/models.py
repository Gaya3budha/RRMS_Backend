from django.db import models

# Create your models here.
# Role Table
class Role(models.Model):
    roleId = models.AutoField(primary_key = True)
    roleName = models.CharField(max_length = 50, unique = True)
    isActive = models.BooleanField(default = True)
    createdOn = models.DateTimeField(auto_now_add = True)
    lastModifiedDate = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.roleName


# DivisionMaster Table
class DivisionMaster(models.Model):
    divisionId = models.AutoField(primary_key = True)
    divisionName = models.CharField(unique = True, max_length = 250)
    active = models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

# State Master
class StateMaster(models.Model):
    stateId = models.AutoField(primary_key = True)
    stateName = models.CharField(unique = True, max_length = 100)
    active =models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

# District Master
class DistrictMaster(models.Model):
    districtId = models.AutoField(primary_key = True)
    districtName = models.CharField( max_length = 100)
    localName = models.CharField(max_length = 200)
    stateId = models.ForeignKey(StateMaster,on_delete=models.SET_NULL, null=True, blank=True,default=None)
    active = models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.districtName

