from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from mdm.models import Role,Designation

# Create your models here.
# User Table
class CustomUserManager(BaseUserManager):
    def create_user(self,kgid,email,password=None, **extra_fields):
        if not kgid:
            raise ValueError('KGID is mandatory')
        email = self.normalize_email(email)
        user = self.model(email=email, kgid = kgid, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,kgid,email,password=None,role=None,designation=None, **extra_fields):
        user = self.create_user(kgid,email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True

        if not role:
            role = Role.objects.get(name="Admin")

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
    # divisionmaster = models.ForeignKey(DivisionMaster, on_delete=models.SET_NULL, null=True, blank=True)
    # division = models.ManyToManyField(DivisionMaster, through = 'UserDivisionRole')
    designation = models.ManyToManyField(Designation,related_name='designation', blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    set_password = models.BooleanField(default = False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'kgid'
    REQUIRED_FIELDS = ['first_name', 'last_name','email','role','divisionmaster','designationmaster']

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

# class UserDivisionRole(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     division = models.ForeignKey(DivisionMaster, on_delete=models.CASCADE)
#     role = models.ForeignKey(Role, on_delete=models.CASCADE)
#     designation = models.ForeignKey(DesignationMaster, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('user', 'division')  # optional

#     def __str__(self):
#         return f"{self.user.first_name}{self.user.last_name} - {self.division.divisionName} - {self.role.roleName} - {self.designation.designationName}"






