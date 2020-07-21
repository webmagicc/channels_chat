from channels.generic.websocket import AsyncJsonWebsocketConsumer, JsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync

from chat.models import Connection


class SendConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        await self.create_connection()

    async def send_message(self, event):
        await self.send_json(content=event)

    @database_sync_to_async
    def create_connection(self):
        Connection.objects.get_or_create(name=self.channel_name)


class SendSyncConsumer(JsonWebsocketConsumer):

    def connect(self):
        self.accept()
        self.create_connection()

    def send_message(self, event):
        self.send_json(content=event)

    def create_connection(self):
        Connection.objects.get_or_create(name=self.channel_name)
