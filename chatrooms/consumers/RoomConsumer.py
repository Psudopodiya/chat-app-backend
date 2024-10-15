import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the 'rooms' group
        await self.channel_layer.group_add(
            "rooms",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the 'rooms' group
        await self.channel_layer.group_discard(
            "rooms",
            self.channel_name
        )

    async def room_created(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "room_created",
            "message": event["message"]
        }))

    async def room_deleted(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "room_deleted",
            "room_id": event["room_id"]
        }))


