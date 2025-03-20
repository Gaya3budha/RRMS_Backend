from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from mdm.models import Role,DivisionMaster

# Create your models here.

# User Table
class CustomUserManager(BaseUserManager):
    def create_user(self,email,kgid,mobileno,password=None):
        if not email:
            raise ValueError('Email is mandatory')
        email = self.normalize_email(email)
        user = self.model(email=email, kgid = kgid, mobileno = mobileno)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,kgid,mobileno, password=None,):
        user = self.create_user(email, employee_id, mobile_no, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    kgid = models.CharField(max_length=20,unique=True,default=None)
    mobileno = models.CharField(max_length=15, unique=True, blank=True, null=True) 
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    divisionmaster = models.ForeignKey(DivisionMaster, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name','kgid','role','division']

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

    def __str__(self):
        return self.email




