from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Проверка прав владельца или администратора.

    Разрешает доступ владельцу объекта или админу.
    """
    def has_object_permission(self, request, view, obj):
        """
        Проверяет, является ли пользователь владельцем или админом.
        """
        return bool(
            request.user.is_authenticated and (
                obj.user == request.user or request.user.is_staff
            )
        )