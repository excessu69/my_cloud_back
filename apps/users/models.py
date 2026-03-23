import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя, расширяющая стандартную модель Django AbstractUser.

    Добавляет поля для полного имени и пути к хранилищу файлов.
    Путь к хранилищу генерируется автоматически при сохранении.
    """
    full_name = models.CharField(
        max_length=255,
        verbose_name='Полное имя',
        blank=True,
    )
    storage_path = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Путь к хранилищу',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def save(self, *args, **kwargs):
        """
        Сохраняет пользователя, автоматически генерируя storage_path если он не задан.

        Генерирует уникальный путь в формате 'users/{username}_{uuid}'.
        """
        if not self.storage_path:
            self.storage_path = f'users/{self.username}_{uuid.uuid4().hex[:8]}'
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Возвращает строковое представление пользователя (username).
        """
        return self.username