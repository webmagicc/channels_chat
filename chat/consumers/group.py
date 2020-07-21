from channels.generic.websocket import AsyncJsonWebsocketConsumer, JsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync

from chat.models import Group


class GroupSendConsumer(AsyncJsonWebsocketConsumer):
    group_name = None

    async def connect(self):
        await self.accept()
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        await self.create_group()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        message = {
            'message': content.get('message', ''),
            'type': 'group.message'
        }
        await self.channel_layer.group_send(self.group_name, message)

    async def group_message(self, event):
        message = {'message': event.get('message', '')}
        await self.send_json(content=message)

    @database_sync_to_async
    def create_group(self):
        Group.objects.get_or_create(name=self.group_name)


class GroupSendSyncConsumer(JsonWebsocketConsumer):
    group_name = None

    def connect(self):
        self.accept()
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.create_group()
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        # self.channel_layer.group_add(self.group_name, self.channel_name)

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)
        # self.channel_layer.group_discard(self.group_name, self.channel_name)

    def receive_json(self, content, **kwargs):
        message = {
            'message': content.get('message', ''),
            'type': 'group.message'
        }
        async_to_sync(self.channel_layer.group_send)(self.group_name, message)
        # await self.channel_layer.group_send(self.group_name, message)

    def group_message(self, event):
        message = {'message': event.get('message', '')}
        self.send_json(content=message)

    def create_group(self):
        Group.objects.get_or_create(name=self.group_name)
