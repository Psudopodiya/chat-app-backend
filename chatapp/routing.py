from django.urls import re_path
from chatrooms.consumers.ChatRoomConsumer import ChatConsumer
from chatrooms.consumers.RoomConsumer import RoomConsumer


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/rooms/$', RoomConsumer.as_asgi()),
]