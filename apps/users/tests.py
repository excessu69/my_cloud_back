from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class AdminAccessTest(APITestCase):
    """
    Тесты для доступа к админ-функциям.
    """

    def setUp(self):
        """
        Создаем обычного пользователя и админа.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='AdminPass123!',
            email='admin@test.com'
        )

    def test_admin_access_users_list(self):
        """
        Тест доступа админа к списку пользователей.
        """
        self.client.force_authenticate(user=self.admin)
        url = reverse('users-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

    def test_user_access_denied_users_list(self):
        """
        Тест отказа доступа обычного пользователя к списку пользователей.
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('users-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserRegistrationTest(APITestCase):
    """
    Тесты для регистрации пользователя.
    """

    def test_user_registration_success(self):
        """
        Тест успешной регистрации пользователя.
        """
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'TestPass123!',
            'full_name': 'Test User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['full_name'], 'Test User')

        user = User.objects.get(username='testuser')
        self.assertEqual(user.full_name, 'Test User')

    def test_user_registration_invalid_username(self):
        """
        Тест регистрации с недопустимым username.
        """
        url = reverse('register')
        data = {
            'username': '123invalid',  
            'password': 'TestPass123!',
            'full_name': 'Test User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(APITestCase):
    """
    Тесты для входа пользователя.
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

    def test_user_login_success(self):
        """
        Тест успешного входа.
        """
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Успешный вход')

    def test_user_login_invalid_credentials(self):
        """
        Тест входа с неверными данными.
        """
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'WrongPass123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
