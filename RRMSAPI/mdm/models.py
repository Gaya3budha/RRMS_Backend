from django.db import models
from django.contrib.auth.models import  Permission

# Create your models here.
# # Permission Table
# class Permission(models.Model):
#     permissionID = models.AutoField(primary_key = True)
#     permissionName = models.CharField(max_length = 100,unique =True)

#     def __str__(self):
#         return self.permissionName

# Role Table
class Role(models.Model):
    roleId = models.AutoField(primary_key = True)
    roleName = models.CharField(max_length = 50, unique = True)
    isActive = models.BooleanField(default = True)
    createdOn = models.DateTimeField(auto_now_add = True)
    lastModifiedDate = models.DateTimeField(auto_now = True)
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.roleName

# Department Table
class Department(models.Model):
    departmentId = models.AutoField(primary_key = True)
    departmentName = models.CharField(unique=True,max_length=150)
    active = models.CharField(default='Y')
    lastModifiedDate = models.DateField(auto_now=True)

    def __str__(self):
        return self.departmentName
    
# DivisionMaster Table
class Division(models.Model):
    divisionId = models.AutoField(primary_key = True)
    departmentId=models.ForeignKey(Department,on_delete= models.CASCADE)
    divisionName = models.CharField(unique = True, max_length = 250)
    active = models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.divisionName
    
# DivisionMaster Table
class DivisionMaster(models.Model):
    divisionId = models.AutoField(primary_key = True)
    divisionName = models.CharField(unique = True, max_length = 250)
    active = models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.divisionName

# State Master
class StateMaster(models.Model):
    stateId = models.AutoField(primary_key = True)
    stateName = models.CharField(unique = True, max_length = 100)
    active =models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.stateName

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
    
class Designation(models.Model):
    designationId = models.AutoField(primary_key = True)
    designationName = models.CharField( max_length = 100)
    active = models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)
    division = models.ManyToManyField(Division)
    department = models.ManyToManyField(Department)

    def __str__(self):
        return self.designationName

# Designation Master
class DesignationMaster(models.Model):
    designationId = models.AutoField(primary_key = True)
    designationName = models.CharField( max_length = 100)
    active = models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.designationName

# Unit Master
class UnitMaster(models.Model):
    unitId = models.AutoField(primary_key = True)
    unitName = models.CharField( max_length = 100)
    stateId = models.ForeignKey(StateMaster,on_delete=models.SET_NULL, null=True, blank=True)
    districtId = models.ForeignKey(DistrictMaster,on_delete=models.SET_NULL, null=True, blank=True)
    typeId = models.IntegerField()
    parentUnit = models.IntegerField()
    actualStrength = models.IntegerField()
    sanctionedStrength = models.IntegerField()
    talukID = models.IntegerField()
    address1 = models.CharField(max_length = 250,blank = True, null = True)
    address2 = models.CharField(max_length = 250,blank = True, null =True)
    active = models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.unitName

# File Classification
class FileClassification(models.Model):
    fileClassificationId = models.AutoField(primary_key = True)
    fileClassificationName = models.CharField( max_length = 100)
    active = models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.fileClassificationName

# File Type
class FileType(models.Model):
    fileTypeId = models.AutoField(primary_key = True)
    fileTypeName = models.CharField( max_length = 100)
    active = models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.fileTypeName

# Case Status
class CaseStatus(models.Model):
    statusId = models.AutoField(primary_key = True)
    statusName = models.CharField( max_length = 100)
    active = models.CharField(default = 'Y')
    lastModifiedDate = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.statusName
    

class GeneralLookUp(models.Model):
    lookupId = models.AutoField(primary_key=True)
    lookupName = models.CharField( max_length= 100)
    CategoryId = models.IntegerField()
    lookupOrder = models.IntegerField(null = True, blank=True)
    active = models.CharField(default ='Y')
    lastmodifiedDate = models.DateTimeField(auto_now= True)