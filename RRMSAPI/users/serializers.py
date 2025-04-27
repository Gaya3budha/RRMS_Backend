import logging
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from mdm.models import Role, DivisionMaster, DesignationMaster
from mdm.serializers import DivisionSerializer,DesignationSerializer,RoleSerializer
from .models import User, UserDivisionRole

# Set up the logger
logger = logging.getLogger(__name__)


class UserDivisionRoleSerializer(serializers.ModelSerializer):
    divisionId = serializers.PrimaryKeyRelatedField(source='division', queryset=DivisionMaster.objects.all())
    roleId = serializers.PrimaryKeyRelatedField(source='role', queryset=Role.objects.all())
    designationId = serializers.PrimaryKeyRelatedField(source='designation', queryset=DesignationMaster.objects.all())

    class Meta:
        model = UserDivisionRole
        fields = ['divisionId', 'roleId', 'designationId']

class UserSerializer(serializers.ModelSerializer):
    # roleId = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role')
    # divisionId = serializers.PrimaryKeyRelatedField(queryset=DivisionMaster.objects.all(), source='divisionmaster')
    # designationId = serializers.PrimaryKeyRelatedField(queryset=DesignationMaster.objects.all(), source='designationmaster')

    divisions_roles = UserDivisionRoleSerializer(source='userdivisionrole_set', many=True)

    class Meta:
        model = User
        fields = ['id','email', 'first_name', 'last_name', 'mobileno', 'kgid', 'password', 'divisions_roles']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        divisions_roles_data = validated_data.pop('userdivisionrole_set', [])
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            mobileno=validated_data.get('mobileno'),
            kgid=validated_data['kgid'],
            password=validated_data['password'],
            # role=validated_data['role'],
            # divisionmaster=validated_data['divisionmaster'],
            # designationmaster=validated_data['designationmaster']
        )

        user.set_password(validated_data['password'])  # password is saved as hash
        user.save()

        for division_role_data in divisions_roles_data:
            UserDivisionRole.objects.create(
                user=user,
                division=division_role_data['division'],
                role=division_role_data['role'],
                designation=division_role_data['designation']
            )

        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Check if it's a GET request by checking the context (the request method)
        # if self.context.get('request') and self.context['request'].method == 'GET':
            # representation['roleName'] = instance.role.roleName if instance.role else None
            # representation['divisionName'] = instance.divisionmaster.divisionName if instance.divisionmaster else None
            # representation['designationName'] = instance.designationmaster.designationName if instance.designationmaster else None
        if self.context.get('request') and self.context['request'].method == 'GET':
            # Flattening division-role-designation info
            representation['divisions_roles'] = [
                {
                    "divisionId": role.division.id,
                    "divisionName": role.division.divisionName,
                    "roleId": role.role.id,
                    "roleName": role.role.roleName,
                    "designationId": role.designation.id,
                    "designationName": role.designation.designationName
                }
                for role in instance.userdivisionrole_set.all()
            ]

        return representation

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # kgid = serializers.CharField()
    # password = serializers.CharField()

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email']=user.email
        token['full_name']=f"{user.first_name} {user.last_name}"

        divisions_roles_data = []
        
        # Fetch user's division-role-designation mappings
        user_division_roles = user.userdivisionrole_set.all()
        
        # role_name = None
        # division_name = None
        # designation_name = None
        # permissions_list = []
        # if user.role_id:
        #     try:
        #         role= Role.objects.get(roleId = user.role_id)
        #         role_name=role.roleName
        #         permissions_list = [perm.codename for perm in role.permissions.all()]
        #     except Role.DoesNotExist:
        #         role_name = "Unknown Role"

        # if user.divisionmaster_id:
        #     try:
        #         division = DivisionMaster.objects.get(divisionId = user.divisionmaster_id)
        #         division_name = division.divisionName
        #     except DivisionMaster.DoesNotExist:
        #         division_name = ""

        # if user.designationmaster_id:
        #     try:
        #         designation = DesignationMaster.objects.get(designationId = user.designationmaster_id)
        #         designation_name = designation.designationName
        #     except DesignationMaster.DoesNotExist:
        #         designation_name = ""

        
        # token['permissions'] = permissions_list
        # token['role_id'] = user.role_id
        # token['role_name']=role_name
        # token['division_id'] = user.divisionmaster_id
        # token['division_name']=division_name
        # token['designation_id']= user.designationmaster_id
        # token['designation_name']=designation_name
        for ur in user_division_roles:
            division_name = ur.division.divisionName if ur.division else ""
            role_name = ur.role.roleName if ur.role else ""
            designation_name = ur.designation.designationName if ur.designation else ""
            permissions_list = [perm.codename for perm in ur.role.permissions.all()] if ur.role else []

            divisions_roles_data.append({
                "division_id": ur.division.divisionId if ur.division else None,
                "division_name": division_name,
                "role_id": ur.role.roleId if ur.role else None,
                "role_name": role_name,
                "designation_id": ur.designation.designationId if ur.designation else None,
                "designation_name": designation_name,
                "permissions": permissions_list
            })
        
        token['divisions_roles'] = divisions_roles_data
        return token
    
class UserDivisionRoleCreateSerializer(serializers.ModelSerializer):
    divisionId = serializers.PrimaryKeyRelatedField(source='division', queryset=DivisionMaster.objects.all())
    roleId = serializers.PrimaryKeyRelatedField(source='role', queryset=Role.objects.all())
    designationId = serializers.PrimaryKeyRelatedField(source='designation', queryset=DesignationMaster.objects.all())

    class Meta:
        model = UserDivisionRole
        fields = ['divisionId', 'roleId', 'designationId']
    

