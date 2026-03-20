from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    MeView,
    LogoutView,
    UserListView,
    UserDeleteView,
    UserAdminUpdateView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('users/', UserListView.as_view(), name='users-list'),
    path('users/<int:id>/', UserAdminUpdateView.as_view(), name='users-update'),
    path('users/<int:id>/delete/', UserDeleteView.as_view(), name='users-delete'),
]