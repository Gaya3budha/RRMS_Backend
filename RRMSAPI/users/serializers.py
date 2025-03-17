from rest_framework import serializers
from .models import User, Role, DistrictMaster

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['roleId','roleName']

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictMaster
        fields = ['districtId','districtName','localName','active','lastModifiedDate']

class UserSerializer(serializers.ModelSerializer):
    roleId = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role')

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'mobileno', 'kgid', 'password', 'roleId']
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
        )

        user.set_password(validated_data['password'])  # password is saved as hash
        user.save()

        return user