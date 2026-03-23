import logging
import os

from django.conf import settings
from django.http import FileResponse, Http404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StoredFile
from .permissions import IsOwnerOrAdmin
from .serializers import (
    StoredFileSerializer,
    FileUploadSerializer,
    FileUpdateSerializer,
)
from .utils import generate_stored_name

logger = logging.getLogger(__name__)


class FileListView(generics.ListAPIView):
    """
    View для получения списка файлов пользователя.

    Админы могут запрашивать файлы других пользователей через query param user_id.
    Обычные пользователи видят только свои файлы.
    """
    serializer_class = StoredFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает queryset файлов в зависимости от прав пользователя.
        """
        user = self.request.user
        target_user_id = self.request.query_params.get('user_id')

        if user.is_staff and target_user_id:
            logger.info(
                'Admin requested file list: admin_id=%s target_user_id=%s',
                user.id,
                target_user_id,
            )
            return StoredFile.objects.filter(user_id=target_user_id).order_by('-uploaded_at')

        logger.info(
            'User requested own file list: user_id=%s',
            user.id,
        )
        return StoredFile.objects.filter(user=user).order_by('-uploaded_at')



class FileUploadView(generics.GenericAPIView):
    """
    View для загрузки файла пользователем.

    Сохраняет файл на диск, создает запись в БД и логирует загрузку.
    """
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Обрабатывает загрузку файла.

        Валидирует данные, сохраняет файл и создает StoredFile объект.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']
        comment = serializer.validated_data.get('comment', '')

        stored_name = generate_stored_name(uploaded_file.name)
        relative_dir = f'users/{request.user.id}'
        absolute_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
        os.makedirs(absolute_dir, exist_ok=True)

        relative_path = os.path.join(relative_dir, stored_name)
        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        with open(absolute_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        stored_file = StoredFile.objects.create(
            user=request.user,
            original_name=uploaded_file.name,
            stored_name=stored_name,
            file_path=relative_path.replace('\\', '/'),
            size=uploaded_file.size,
            comment=comment,
        )

        logger.info(
            'File uploaded: file_id=%s user_id=%s name=%s size=%s',
            stored_file.id,
            request.user.id,
            stored_file.original_name,
            stored_file.size,
        )

        return Response(
            StoredFileSerializer(stored_file).data,
            status=status.HTTP_201_CREATED
        )


class FileDeleteView(generics.DestroyAPIView):
    """
    View для удаления файла.

    Удаляет файл с диска и из БД. Доступен владельцу или админу.
    """
    queryset = StoredFile.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        """
        Удаляет файл с диска и логирует событие.
        """
        absolute_path = os.path.join(settings.MEDIA_ROOT, instance.file_path)

        if os.path.exists(absolute_path):
            os.remove(absolute_path)

        logger.info(
            'File deleted: file_id=%s user_id=%s name=%s',
            instance.id,
            instance.user.id,
            instance.original_name,
        )

        instance.delete()


class FileUpdateView(generics.UpdateAPIView):
    """
    View для обновления файла (комментария).

    Позволяет изменять комментарий к файлу. Доступен владельцу или админу.
    """
    queryset = StoredFile.objects.all()
    serializer_class = FileUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'id'

    def perform_update(self, serializer):
        """
        Обновляет файл и логирует изменения.
        """
        file = serializer.save()

        logger.info(
            'File updated: file_id=%s user_id=%s name=%s comment=%s',
            file.id,
            file.user.id,
            file.original_name,
            file.comment,
        )        


class FileDownloadView(generics.GenericAPIView):
    """
    View для скачивания файла.

    Возвращает файл как attachment. Доступен владельцу или админу.
    Обновляет дату последнего скачивания.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'id'

    def get(self, request, id):
        try:
            file = StoredFile.objects.get(id=id)
        except StoredFile.DoesNotExist:
            raise Http404

        self.check_object_permissions(request, file)

        absolute_path = os.path.join(settings.MEDIA_ROOT, file.file_path)

        if not os.path.exists(absolute_path):
            raise Http404

        file.last_downloaded_at = timezone.now()
        file.save(update_fields=['last_downloaded_at'])

        logger.info(
            'File downloaded: file_id=%s user_id=%s name=%s',
            file.id,
            request.user.id,
            file.original_name,
        )

        return FileResponse(
            open(absolute_path, 'rb'),
            as_attachment=True,
            filename=file.original_name,
        )
    


class FilePublicLinkView(APIView):
    """
    View для генерации публичной ссылки на файл.

    POST: возвращает публичную ссылку.
    GET: показывает ссылку (для совместимости).
    Доступен владельцу или админу.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, id):
        try:
            file = StoredFile.objects.get(id=id)
        except StoredFile.DoesNotExist:
            raise Http404

        self.check_object_permissions(request, file)

        link = f'/api/files/public/{file.public_token}/'

        logger.info(
            'Public link requested: file_id=%s user_id=%s token=%s',
            file.id,
            request.user.id,
            file.public_token,
        )

        return Response({
            'public_url': link
        }, status=status.HTTP_200_OK)

    def get(self, request, id):
        try:
            file = StoredFile.objects.get(id=id)
        except StoredFile.DoesNotExist:
            raise Http404

        self.check_object_permissions(request, file)

        link = f'/api/files/public/{file.public_token}/'

        logger.info(
            'Public link viewed: file_id=%s user_id=%s token=%s',
            file.id,
            request.user.id,
            file.public_token,
        )

        return Response({
            'detail': 'Используйте POST для получения публичной ссылки.',
            'public_url': link
        }, status=status.HTTP_200_OK)
    


class PublicFileDownloadView(generics.GenericAPIView):
    """
    View для публичного скачивания файла по токену.

    Не требует аутентификации, доступ по публичному токену.
    """
    permission_classes = []

    def get(self, request, token):
        try:
            file = StoredFile.objects.get(public_token=token)
        except StoredFile.DoesNotExist:
            raise Http404

        absolute_path = os.path.join(settings.MEDIA_ROOT, file.file_path)

        if not os.path.exists(absolute_path):
            raise Http404

        file.last_downloaded_at = timezone.now()
        file.save(update_fields=['last_downloaded_at'])

        logger.info(
            'Public file downloaded: file_id=%s token=%s name=%s',
            file.id,
            file.public_token,
            file.original_name,
        )

        return FileResponse(
            open(absolute_path, 'rb'),
            as_attachment=True,
            filename=file.original_name,
        )