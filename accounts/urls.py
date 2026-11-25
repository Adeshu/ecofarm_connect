# accounts/urls.py
from django.urls import path, register_converter
from . import views
import uuid

app_name = 'accounts'
class UUIDConverter:
    regex = '[0-9a-f-]{36}'

    def to_python(self, value):
        return uuid.UUID(value)

    def to_url(self, value):
        return str(value)
register_converter(UUIDConverter, 'uuid')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('user/<uuid:user_id>/', views.user_detail, name='user_detail'),
    
]
