import uuid

from django.conf import settings
from django.db import models


class StoredFile(models.Model):
    """
    Модель для хранения информации о загруженных файлах пользователей.

    Содержит метаданные файла, включая оригинальное и сохраненное имя,
    путь, размер, комментарий, даты и токен для публичного доступа.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Владелец'
    )
    original_name = models.CharField(
        max_length=255,
        verbose_name='Оригинальное имя файла'
    )
    stored_name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Имя файла на диске'
    )
    file_path = models.CharField(
        max_length=500,
        unique=True,
        verbose_name='Путь к файлу'
    )
    size = models.PositiveBigIntegerField(
        verbose_name='Размер файла в байтах'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )
    last_downloaded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата последнего скачивания'
    )
    public_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='Публичный токен'
    )

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.original_name} ({self.user.username})'