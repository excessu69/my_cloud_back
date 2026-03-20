from rest_framework import serializers

from .models import StoredFile


class StoredFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoredFile
        fields = (
            'id',
            'original_name',
            'size',
            'comment',
            'uploaded_at',
            'last_downloaded_at',
            'public_token',
        )


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    comment = serializers.CharField(required=False, allow_blank=True)


class FileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoredFile
        fields = ('original_name', 'comment')    