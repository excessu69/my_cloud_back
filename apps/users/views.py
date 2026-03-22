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
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(
            'User registered: id=%s username=%s email=%s',
            user.id,
            user.username,
            user.email
        )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
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
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProfileUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        user = serializer.save()
        logger.info(
            'Profile updated: user_id=%s username=%s full_name=%s',
            user.id,
            user.username,
            user.full_name,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {'detail': 'Используйте POST для выхода из системы.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def post(self, request):
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
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_queryset(self):
        return User.objects.annotate(
            files_count=Count('files'),
            files_total_size=Coalesce(Sum('files__size'), Value(0)),
        ).order_by('id')


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        logger.info(
            'User deleted by admin: admin_id=%s deleted_user_id=%s deleted_username=%s',
            self.request.user.id,
            instance.id,
            instance.username,
        )
        instance.delete()


class UserAdminUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserAdminUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    lookup_field = 'id'

    def perform_update(self, serializer):
        user = serializer.save()
        logger.info(
            'User updated by admin: admin_id=%s updated_user_id=%s is_staff=%s',
            self.request.user.id,
            user.id,
            user.is_staff,
        )

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        user = serializer.save()
        logger.info(
            'Password changed: user_id=%s username=%s',
            user.id,
            user.username,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'message': 'Пароль успешно изменен'}, status=status.HTTP_200_OK)