from django.urls import re_path
from chatrooms.consumer import ChatConsumer, RoomConsumer


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/rooms/$', RoomConsumer.as_asgi()),
]