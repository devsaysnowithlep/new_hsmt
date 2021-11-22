from django.db.models import fields
from rest_framework import serializers
from xfiles.models import *

class ExContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExContent
        fields = ('id', 'name')

class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detail
        fields = ('id', 'timestamp', 'text')

class ContentSerializer(serializers.ModelSerializer):
    details = DetailSerializer(many=True)
    class Meta:
        model = Content
        fields = ('id', 'name', 'details')
        read_only_fields = ('name',)

class XFileTypeSerializer(serializers.ModelSerializer):
    ex_contents = ExContentSerializer(many=True)
    class Meta:
        model = XFileType
        fields = ('id', 'name', 'slug', 'ex_contents')

    def create(self, validated_data):
        ex_contents = validated_data.pop('ex_contents')
        xfile_type = XFileType.objects.create(**validated_data)
        for ex_content in ex_contents:
            ExContent.objects.create(xfile_type=xfile_type, **ex_content)
        return xfile_type

    def update(self, instance, validated_data):
        ex_contents = validated_data.pop('ex_contents')
        instance = super().update(instance, validated_data)
        instance.ex_contents.all().delete()
        for ex_content in ex_contents:
            ExContent.objects.create(xfile_type=instance, **ex_content)
        return instance

class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ('id', 'name', 'get_type_display', 'description', 'type')
        read_only_fields = ('get_type_display', )

class AttackLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttackLog
        fields = ('id', 'timestamp', 'process', 'result', 'attacker')

class XFileLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = XFileLog
        fields = ('id', 'timestamp', 'action', 'performer', 'contents', 'attack_logs', 'get_action_display')
        read_only_fields = ('timestamp', 'performer', 'get_action_display')

class XFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = XFile
        fields = ('id', 'status', 'get_status_display', 'code', 'description', 'type', 'targets', 'department', 'editors', 'date_created', 'contents', 'attack_logs', 'submitted_by', 'approved_by', 'date_submitted', 'date_approved')
        read_only_fields = ('status', 'get_status_display', 'date_created', 'contents', 'attacklogs', 'submitted_by', 'approved_by', 'date_submitted', 'date_approved')

# class XFileDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = XFile
#         fields = ('id', 'code', 'contents')
# 
# class XFileFullSerializer(serializers.ModelSerializer):
#     contents = ContentSerializer(many=True)
#     attack_logs = AttackLogSerializer(many=True)
#     class Meta:
#         model = XFile
#         fields = ('code', 'description', 'targets', 'contents', 'attack_logs')

