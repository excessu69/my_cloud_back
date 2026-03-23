from rest_framework import serializers

from .models import StoredFile


class StoredFileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о файле.
    """
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
    """
    Сериализатор для загрузки файла.

    Принимает файл и опциональный комментарий.
    """
    file = serializers.FileField()
    comment = serializers.CharField(required=False, allow_blank=True)


class FileUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления файла (имя и комментарий).
    """
    class Meta:
        model = StoredFile
        fields = ('original_name', 'comment')    