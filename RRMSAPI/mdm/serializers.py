import logging
from rest_framework import serializers
from .models import  Role, DistrictMaster, DivisionMaster, StateMaster

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateMaster
        fields = ['stateId','stateName','active','lastModifiedDate']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['roleId','roleName']

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictMaster
        fields = ['districtId','districtName','localName','active','lastModifiedDate']

class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DivisionMaster
        fields = ['divisionId','divisionName','active','lastModifiedDate']

