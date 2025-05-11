from django.contrib import admin
from .models import User
# UserDivisionRole

# class UserDivisionRoleInline(admin.TabularInline):  # or admin.StackedInline
#     model = UserDivisionRole
#     extra = 1
#     autocomplete_fields = ['division', 'role', 'designation']  # improves usability
#     show_change_link = True

# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ['kgid','first_name', 'last_name', 'email','is_staff','last_login']
#     readonly_fields = ['is_staff']
#     inlines = [UserDivisionRoleInline]

# Register your models here.
# admin.site.register(User, CustomUserAdmin)
admin.site.register(User)
# admin.site.register(UserDivisionRole)