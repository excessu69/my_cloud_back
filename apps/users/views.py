import logging

from django.contrib.auth import get_user_model, login, logout
from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from .permissions import IsAdminUserCustom
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserListSerializer,
    UserAdminUpdateSerializer,
    ChangePasswordSerializer,
    ProfileUpdateSerializer,
)

logger = logging.getLogger(__name__)

User = get_user_model()


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfView(APIView):
    """
    View для установки CSRF cookie.

    Возвращает ответ с установленным CSRF токеном.
    """
    def get(self, request):
        """
        Обрабатывает GET запрос для установки CSRF cookie.
        """
        return Response({'detail': 'CSRF cookie set'})


class RegisterView(generics.CreateAPIView):
    """
    View для регистрации нового пользователя.

    Принимает POST запрос с данными пользователя.
    Создает нового пользователя и логирует событие.
    """
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        """
        Создает пользователя и логирует регистрацию.
        """
        user = serializer.save()
        logger.info(
            'User registered: id=%s username=%s email=%s',
            user.id,
            user.username,
            user.email
        )


class LoginView(generics.GenericAPIView):
    """
    View для входа пользователя в систему.

    Принимает POST запрос с username и password.
    Выполняет аутентификацию и логирует вход.
    """
    serializer_class = LoginSerializer

    def post(self, request):
        """
        Обрабатывает POST запрос для входа.

        Валидирует данные, выполняет вход и возвращает ответ.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)

        logger.info(
            'User logged in: id=%s username=%s',
            user.id,
            user.username
        )

        return Response({
            'message': 'Успешный вход'
        }, status=status.HTTP_200_OK)
    

class MeView(generics.RetrieveUpdateAPIView):
    """
    View для получения и обновления профиля текущего пользователя.

    GET: возвращает данные пользователя.
    PUT/PATCH: обновляет профиль (никнейм, имя).
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от метода запроса.
        """
        if self.request.method in ['PUT', 'PATCH']:
            return ProfileUpdateSerializer
        return UserSerializer

    def get_object(self):
        """
        Возвращает текущего аутентифицированного пользователя.
        """
        return self.request.user

    def perform_update(self, serializer):
        """
        Обновляет профиль пользователя и логирует изменения.
        """
        user = serializer.save()
        logger.info(
            'Profile updated: user_id=%s username=%s full_name=%s',
            user.id,
            user.username,
            user.full_name,
        )


class LogoutView(APIView):
    """
    View для выхода пользователя из системы.

    Принимает POST запрос для выполнения logout.
    Логирует выход пользователя.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Обрабатывает GET запрос, возвращает ошибку метода.
        """
        return Response(
            {'detail': 'Используйте POST для выхода из системы.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def post(self, request):
        """
        Выполняет выход пользователя из системы.
        """
        user = request.user

        logout(request)

        logger.info(
            'User logged out: id=%s username=%s',
            user.id,
            user.username
        )

        return Response({
            'message': 'Успешный выход'
        }, status=status.HTTP_200_OK)
    

class UserListView(generics.ListAPIView):
    """
    View для получения списка всех пользователей (только для админов).

    Возвращает пользователей с аннотациями: количество файлов и общий размер.
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_queryset(self):
        """
        Возвращает queryset пользователей с аннотациями.
        """
        return User.objects.annotate(
            files_count=Count('files'),
            files_total_size=Coalesce(Sum('files__size'), Value(0)),
        ).order_by('id')


class UserDeleteView(generics.DestroyAPIView):
    """
    View для удаления пользователя (только для админов).

    Удаляет пользователя и логирует действие.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        """
        Удаляет пользователя и логирует событие.
        """
        logger.info(
            'User deleted by admin: admin_id=%s deleted_user_id=%s deleted_username=%s',
            self.request.user.id,
            instance.id,
            instance.username,
        )
        instance.delete()


class UserAdminUpdateView(generics.UpdateAPIView):
    """
    View для обновления пользователя админом (только для админов).

    Позволяет изменять статус staff и другие поля.
    """
    queryset = User.objects.all()
    serializer_class = UserAdminUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    lookup_field = 'id'

    def perform_update(self, serializer):
        """
        Обновляет пользователя и логирует изменения.
        """
        user = serializer.save()
        logger.info(
            'User updated by admin: admin_id=%s updated_user_id=%s is_staff=%s',
            self.request.user.id,
            user.id,
            user.is_staff,
        )

class ChangePasswordView(generics.UpdateAPIView):
    """
    View для изменения пароля текущего пользователя.

    Принимает старый и новый пароль, валидирует и обновляет.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Возвращает текущего пользователя.
        """
        return self.request.user

    def perform_update(self, serializer):
        """
        Изменяет пароль и логирует событие.
        """
        user = serializer.save()
        logger.info(
            'Password changed: user_id=%s username=%s',
            user.id,
            user.username,
        )

    def update(self, request, *args, **kwargs):
        """
        Обрабатывает запрос на изменение пароля с кастомным ответом.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'message': 'Пароль успешно изменен'}, status=status.HTTP_200_OK)