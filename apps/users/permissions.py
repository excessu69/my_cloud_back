from rest_framework.permissions import BasePermission


class IsAdminUserCustom(BasePermission):
    """
    Проверка прав администратора.

    Разрешает доступ только аутентифицированным пользователям с is_staff=True.
    """
    def has_permission(self, request, view):
        """
        Проверяет, является ли пользователь админом.
        """
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
    

    