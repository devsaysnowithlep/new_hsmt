from rest_framework import serializers
from users.models import *

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'slug')

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id', 'name', 'slug')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'address', 'skill', 'phone_number', 'self_introduction', 'email', 'layout_config')

class UserManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'is_active', 'department', 'position')

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'address', 'skill', 'phone_number', 'self_introduction', 'email', 'layout_config', 'date_joined', 'last_login', 'department', 'position', 'is_active')
        read_only_fields = ('id', 'address', 'skill', 'phone_number', 'self_introduction', 'email', 'layout_config', 'date_joined', 'last_login', 'is_active')