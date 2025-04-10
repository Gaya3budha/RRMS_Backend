from django.contrib import admin
from .models import Role,DivisionMaster
from django.contrib.auth.models import  Permission

# Register your models here.
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(DivisionMaster)