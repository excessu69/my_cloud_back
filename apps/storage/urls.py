from django.urls import path

from .views import (
    FileListView,
    FileUploadView,
    FileDeleteView,
    FileUpdateView,
    FileDownloadView,
    FilePublicLinkView,
    PublicFileDownloadView,
)

urlpatterns = [
    path('', FileListView.as_view(), name='file-list'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('<int:id>/', FileUpdateView.as_view(), name='file-update'),
    path('<int:id>/delete/', FileDeleteView.as_view(), name='file-delete'),
    path('<int:id>/download/', FileDownloadView.as_view(), name='file-download'),
    path('<int:id>/public-link/', FilePublicLinkView.as_view(), name='file-public-link'),
    path('public/<uuid:token>/', PublicFileDownloadView.as_view(), name='public-download'),
]