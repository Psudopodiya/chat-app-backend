from django.urls import path
from .views import register, profile, edit_profile, list_users

urlpatterns = [
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('list/', list_users, name='list_users'),
]
