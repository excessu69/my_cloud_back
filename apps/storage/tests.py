from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
import tempfile
import os

from .models import StoredFile

User = get_user_model()


class FileUploadTest(APITestCase):
    """
    Тесты для загрузки файла.
    """

    def setUp(self):
        """
        Создаем тестового пользователя.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        self.client.force_authenticate(user=self.user)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_file_upload_success(self):
        """
        Тест успешной загрузки файла.
        """
        url = reverse('file-upload')
        file_content = b'This is a test file content.'
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            file_content,
            content_type='text/plain'
        )
        data = {
            'file': uploaded_file,
            'comment': 'Test comment'
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['original_name'], 'test.txt')
        self.assertEqual(response.data['comment'], 'Test comment')
        file_obj = StoredFile.objects.get(id=response.data['id'])
        self.assertEqual(file_obj.user, self.user)
        self.assertEqual(file_obj.size, len(file_content))


class FileDownloadTest(APITestCase):
    """
    Тесты для скачивания файла.
    """

    def setUp(self):
        """
        Создаем тестового пользователя и файл.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        self.client.force_authenticate(user=self.user)

        self.file_obj = StoredFile.objects.create(
            user=self.user,
            original_name='test.txt',
            stored_name='stored_test.txt',
            file_path='users/1/stored_test.txt',
            size=100,
            comment='Test file'
        )

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_file_download_success(self):
        """
        Тест успешного скачивания файла.
        """
        media_root = tempfile.mkdtemp()
        file_path = os.path.join(media_root, self.file_obj.file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(b'This is test content')

        with override_settings(MEDIA_ROOT=media_root):
            url = reverse('file-download', kwargs={'id': self.file_obj.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Disposition'], f'attachment; filename="{self.file_obj.original_name}"')

    def test_file_download_not_found(self):
        """
        Тест скачивания несуществующего файла.
        """
        url = reverse('file-download', kwargs={'id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
