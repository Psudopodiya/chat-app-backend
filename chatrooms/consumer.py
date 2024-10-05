import jwt
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.conf import settings
from urllib.parse import urljoin


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Extract subprotocols from the WebSocket connection (Sec-WebSocket-Protocol)
        subprotocols = self.scope['subprotocols']

        # Check if subprotocols are present
        if len(subprotocols) >= 2:
            real_protocol = subprotocols[0]  # The real WebSocket protocol
            token = subprotocols[1]  # The token sent by the client
        else:
            token = None  # No token provided

        if token:
            try:
                # Decode the token
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload['user_id']

                # Get the user
                self.user = await self.get_user(user_id)

                if self.user:
                    # Join the room group if the user is valid
                    await self.channel_layer.group_add(
                        self.room_group_name,
                        self.channel_name
                    )
                    await self.accept(subprotocol=real_protocol)  # Accept with the real protocol
                else:
                    # Close the connection if the user is not found
                    await self.close()
            except jwt.ExpiredSignatureError:
                # Handle expired token
                await self.close()
            except jwt.InvalidTokenError:
                # Handle invalid token
                await self.close()
        else:
            # Close the connection if no token is provided
            await self.close()

    async def get_user(self, user_id):
        return await database_sync_to_async(self._get_user)(user_id)

    def _get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        # Leave the room group when the WebSocket connection is closed
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Helper function to construct absolute URLs

    def build_absolute_uri(self, relative_url):
        # Construct the full media URL by joining MEDIA_URL with the profile image's relative URL
        return urljoin(f"http://127.0.0.1:8000{settings.MEDIA_URL}", relative_url)

    # Receive a message from the WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Construct the profile image URL
        profile_image = self.build_absolute_uri(self.user.profile_image.url) if self.user.profile_image else None

        # Send the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'profile_image': profile_image
            }
        )

    # Receive a message from the room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        profile_image = event['profile_image']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'profile_image_url': profile_image
        }))
