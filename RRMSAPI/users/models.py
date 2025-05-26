from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from mdm.models import Role,Designation
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

# Create your models here.
# User Table
class CustomUserManager(BaseUserManager):
    def create_user(self,kgid,email,password=None,role=None,designation=None, **extra_fields):
        if not kgid:
            raise ValueError('KGID is mandatory')
        # email = self.normalize_email(email)
        user = self.model(email=email, kgid = kgid, role=role, **extra_fields)

        if role and role.roleId == 1:
            admin_count = User.objects.filter(is_superuser=True,is_active=True).count()
            print("admin_count:",admin_count)
            if admin_count >= 5:
                raise ValidationError("Cannot create more than 5 admin users.")

            user.is_staff = True
            user.is_superuser = True

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,kgid,email,password=None,role=None,designation=None, **extra_fields):
        

        if not role:
            role = Role.objects.get(roleId=1)

        active_admin_count = User.objects.filter(is_superuser=True, is_active=True).count()
        if active_admin_count >= 5:
            raise ValidationError("Cannot create more than 5 active admin users.")
        
        user = self.model(
            kgid=kgid,
            email=email,
            role=role,
            is_staff=True,
            is_superuser=True,
            **extra_fields
        )

        # user = self.create_user(kgid, email, password, role=role, designation=designation, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):

    kgid = models.CharField(max_length=20,unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    mobileno = models.CharField(max_length=15, unique=True, blank=True, null=True) 
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ManyToManyField(Designation,related_name='designation', blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_passwordset = models.BooleanField(default = False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'kgid'
    REQUIRED_FIELDS = ['first_name', 'last_name','email','role']

    # Modify the 'groups' relationship by specifying a custom 'related_name'
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    # Add custom related_name to avoid conflict for user_permissions
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def save(self,*args,**kwargs):
            if self.role and self.role.roleId == 1 and self.is_active:
                active_admin_count = User.objects.filter(is_superuser=True, is_active=True, role__roleId=1)
                print("active_admin_count",active_admin_count)
                if self.pk:
                    # Exclude self if updating
                    active_admin_count = active_admin_count.exclude(pk=self.pk)

                if active_admin_count.count() >= 5 and self.is_superuser:
                    raise ValidationError("Cannot create or activate more than 5 admin users.")

            super().save(*args, **kwargs)

    def __str__(self):
        return self.kgid

    def has_permissions(self, permission_codename):

        if self.role:
            return self.role.permissions.filter(codename = permission_codename).exists()
        
        return False

class ActiveUser(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.kgid

class PasswordResetOTP(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)
    
class PasswordResetRequest(models.Model):
    passwordResetRequestId = models.AutoField(primary_key=True)
    kgid = models.CharField()
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    email = models.EmailField()
    mobileno=models.CharField(max_length=10)
    requested_at = models.DateTimeField(auto_now_add=True)
    requested_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.kgid} - {self.email}-{self.mobileno}"




