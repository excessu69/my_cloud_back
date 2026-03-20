from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'full_name',
        'storage_path',
        'is_staff',
        'is_superuser',
        'is_active',
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
    )
    search_fields = (
        'username',
        'email',
        'full_name',
    )
    ordering = ('id',)

    fieldsets = UserAdmin.fieldsets + (
        (
            'Дополнительная информация',
            {
                'fields': (
                    'full_name',
                    'storage_path',
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Дополнительная информация',
            {
                'fields': (
                    'full_name',
                    'storage_path',
                ),
            },
        ),
    )