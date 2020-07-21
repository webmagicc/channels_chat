from channels.generic.websocket import JsonWebsocketConsumer, AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


class MiddlewareSessionConsumer(JsonWebsocketConsumer):
    def receive_json(self, content, **kwargs):
        self.scope['session']['message'] = 'Work with session from consumer'
        self.scope['session'].save()
        self.send_json(content={'message': self.scope['session'].get('message', None)})


class AsyncMiddlewareSessionConsumer(AsyncJsonWebsocketConsumer):
    async def receive_json(self, content, **kwargs):
        self.scope['session']['message'] = 'Work with session from async consumer'
        await self.session_save()
        await self.send_json(content={'message': self.scope['session'].get('message', None)})

    @database_sync_to_async
    def session_save(self):
        self.scope['session'].save()



