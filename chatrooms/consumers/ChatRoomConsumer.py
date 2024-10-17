import jwt
import json
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.conf import settings
from urllib.parse import urljoin
from chatrooms.models import ChatMessage, ChatRoom

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_id = f'chat_{self.room_id}'
        self.user = None

        if await self.authenticate():
            await self.join_room()
            await self.send_chat_history()
        else:
            await self.close()

    async def authenticate(self):
        token = self.get_token_from_subprotocol()
        if not token:
            logger.warning("No token provided")
            return False

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            self.user = await self.get_user(payload['user_id'])
            return bool(self.user)
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token")
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
        return False

    def get_token_from_subprotocol(self):
        subprotocols = self.scope['subprotocols']
        return subprotocols[1] if len(subprotocols) >= 2 else None

    async def join_room(self):
        self.room = await self.get_room(self.room_id)
        if not self.room:
            logger.warning(f"Room with id {self.room_id} does not exist")
            await self.close()
            return

        if self.user:
            if self.room.room_type == 'public':
                await self.channel_layer.group_add(self.room_group_id, self.channel_name)
                await self.accept(subprotocol=self.scope['subprotocols'][0])
                logger.info(f"User {self.user.username} joined room {self.room_id}")
            elif self.room.room_type == 'private':
                if await self.is_room_participant(self.user, self.room):
                    await self.channel_layer.group_add(self.room_group_id, self.channel_name)
                    await self.accept(subprotocol=self.scope['subprotocols'][0])
                    logger.info(f"User {self.user.username} joined private room {self.room_id}")
                else:
                    logger.warning(f"User {self.user.username} not allowed in private room {self.room_id}")
                    await self.close()
            elif self.room.room_type == 'one-to-one':
                if await self.is_room_participant(self.user, self.room):
                    await self.channel_layer.group_add(self.room_group_id, self.channel_name)
                    await self.accept(subprotocol=self.scope['subprotocols'][0])
                    logger.info(f"User {self.user.username} joined one-to-one room {self.room_id}")
                else:
                    logger.warning(f"User {self.user.username} not allowed in one-to-one room {self.room_id}")
                    await self.close()
            else:
                logger.warning(f"Room type {self.room.room_type} is not recognized")
                await self.close()
        else:
            logger.warning(f"User {self.user.username} not allowed in room {self.room_id}")
            await self.close()

    async def send_chat_history(self):
        messages = await self.get_chat_messages(self.room_id)
        for message in messages:
            await self.send(text_data=json.dumps(message))
        logger.info(f"Sent {len(messages)} messages from chat history")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_id'):
            await self.channel_layer.group_discard(self.room_group_id, self.channel_name)
        logger.info(f"User disconnected from room {self.room_id}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        await self.save_and_broadcast_message(message)

    async def save_and_broadcast_message(self, message):
        profile_image = self.build_absolute_uri(self.user.profile_image.url) if self.user.profile_image else None
        timestamp = datetime.now().isoformat()

        await self.save_message(self.room_id, self.user, message)
        await self.channel_layer.group_send(
            self.room_group_id,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'profile_image': profile_image,
                'timestamp': timestamp
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    def build_absolute_uri(self, relative_url):
        return urljoin(f"http://127.0.0.1:8001{settings.MEDIA_URL}", relative_url)

    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_room(self, room_id):
        try:
            return ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def is_room_participant(self, user, room):
        return room.participants.filter(id=user.id).exists()

    @database_sync_to_async
    def get_chat_messages(self, room_id):
        messages = ChatMessage.objects.filter(room__id=room_id).order_by('timestamp')[:50]
        return [
            {
                'message': msg.content,
                'username': msg.user.username,
                'profile_image_url': self.build_absolute_uri(
                    msg.user.profile_image.url) if msg.user.profile_image else None,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]

    @database_sync_to_async
    def save_message(self, room_id, user, content):
        ChatMessage.objects.create(room_id=room_id, user=user, content=content)

    # Receive a message from the room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        profile_image = event['profile_image']
        timestamp = event['timestamp']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'profile_image_url': profile_image,
            'timestamp': timestamp,
        }))
