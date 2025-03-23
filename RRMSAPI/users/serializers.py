import logging
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from mdm.models import Role, DivisionMaster, DesignationMaster
from .models import User

# Set up the logger
logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    roleId = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role')
    divisionId = serializers.PrimaryKeyRelatedField(queryset=DivisionMaster.objects.all(), source='divisionmaster')
    designationId = serializers.PrimaryKeyRelatedField(queryset=DesignationMaster.objects.all(), source='designationmaster')

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'mobileno', 'kgid', 'password', 'roleId','divisionId','designationId']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):

        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            mobileno=validated_data.get('mobileno'),
            kgid=validated_data['kgid'],
            password=validated_data['password'],
            role=validated_data['role'],
            divisionmaster=validated_data['divisionmaster'],
            designationmaster=validated_data['designationmaster']
        )

        user.set_password(validated_data['password'])  # password is saved as hash
        user.save()

        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Check if it's a GET request by checking the context (the request method)
        if self.context.get('request') and self.context['request'].method == 'GET':
            representation['roleName'] = instance.role.roleName if instance.role else None
            representation['divisionName'] = instance.divisionmaster.divisionName if instance.divisionmaster else None
            representation['designationName'] = instance.designationmaster.designationName if instance.designationmaster else None

        return representation

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email']=user.email
        token['role'] = user.role_id
        token['full_name']=f"{user.first_name} {user.last_name}"

        return token
