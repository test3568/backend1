import ujson
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings


class WsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(
            settings.CHANNEL_GROUP_NAME,
            self.channel_name
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            settings.CHANNEL_GROUP_NAME,
            self.channel_name
        )

    async def group_message(self, event):
        await self.send(text_data=ujson.dumps({
            'message': event['message']
        }))
