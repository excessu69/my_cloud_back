from django.contrib import admin

from .models import StoredFile


@admin.register(StoredFile)
class StoredFileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'original_name',
        'user',
        'size',
        'uploaded_at',
        'last_downloaded_at',
    )
    list_filter = (
        'uploaded_at',
        'last_downloaded_at',
    )
    search_fields = (
        'original_name',
        'user__username',
        'user__email',
    )
    ordering = ('-uploaded_at',)
    readonly_fields = (
        'uploaded_at',
        'last_downloaded_at',
        'public_token',
    )