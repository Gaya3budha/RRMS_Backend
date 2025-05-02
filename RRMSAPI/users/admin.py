from django.contrib import admin
from .models import User, UserDivisionRole

# Register your models here.
admin.site.register(User)
admin.site.register(UserDivisionRole)