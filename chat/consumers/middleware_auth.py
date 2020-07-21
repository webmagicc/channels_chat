from channels.generic.websocket import JsonWebsocketConsumer, AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.auth import login, logout
from django.contrib.auth import get_user_model


User = get_user_model()


class MiddlewareAuthConsumer(JsonWebsocketConsumer):
    def receive_json(self, content, **kwargs):
        # user = User.objects.get(username='user1')
        # async_to_sync(login)(self.scope, user)
        # self.scope["session"].save()
        for k, v in self.scope["session"].items():
            print(k, v)
        for k, v in self.scope.items():
            print(k, v)
        self.send_json(content={'message': str(self.scope['user'])})


class AsyncMiddlewareAuthConsumer(AsyncJsonWebsocketConsumer):
    async def receive_json(self, content, **kwargs):
        user = await self.get_user()
        await login(self.scope, user)
        await self.session_save()
        await self.send_json(content={'message': str(self.scope['user'])})

    @database_sync_to_async
    def session_save(self):
        self.scope['session'].save()

    @database_sync_to_async
    def get_user(self):
        return User.objects.get(username='user1')
