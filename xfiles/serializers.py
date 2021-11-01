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

class XFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = XFile
        fields = ('id', 'code', 'description', 'type', 'date_created', 'contents')
        read_only_fields = ('contents',)

class XFileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = XFile
        fields = ('id', 'code', 'contents')
