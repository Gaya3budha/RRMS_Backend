from django.contrib import admin
from .models import Role,DivisionMaster, FileType, FileClassification, CaseStatus, DesignationMaster, UnitMaster
from django.contrib.auth.models import  Permission
from django.contrib.auth.models import Group

# Register your models here.
# admin.site.register(Role)
# admin.site.register(Permission)
# admin.site.register(DivisionMaster)
admin.site.register(FileType)
admin.site.register(FileClassification)
admin.site.register(CaseStatus)
admin.site.unregister(Group)
admin.site.register(UnitMaster)

@admin.register(DivisionMaster)
class DivisionMasterAdmin(admin.ModelAdmin):
    search_fields = ['divsionId','divisionName','active']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = ['roleName']

@admin.register(DesignationMaster)
class DesignationMasterAdmin(admin.ModelAdmin):
    search_fields = ['designationName']
