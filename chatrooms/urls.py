from django.urls import path
from .views import list_rooms, create_room, join_room

urlpatterns = [
    path('rooms/', list_rooms, name='list_rooms'),
    path('rooms/create/', create_room, name='create_room'),
    path('rooms/join/<int:room_id>/', join_room, name='join_room'),
]