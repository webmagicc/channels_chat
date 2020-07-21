import json

from channels.generic.websocket import (WebsocketConsumer, AsyncWebsocketConsumer,
                                        JsonWebsocketConsumer, AsyncJsonWebsocketConsumer)
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer


class BaseSyncConsumer(SyncConsumer):
    def websocket_connect(self, event):
        self.send({
            "type": "websocket.accept"
        })

    def websocket_receive(self, event):
        self.send({
            "type": "websocket.send",
            "text": str(event)
        })

    def websocket_disconnect(self):
        raise StopConsumer()


class BaseAsyncConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    async def websocket_disconnect(self):
        raise StopConsumer()


class WsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):

        json_data = json.loads(text_data)
        message = json_data.get('message')
        message2 = json_data.get('message2')
        self.send(text_data=json.dumps({
            'received_message': message,
            'received_message2': message2
        }))
        # self.send(text_data=text_data)


class WsAsyncConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):

        json_data = json.loads(text_data)
        message = json_data.get('message')
        message2 = json_data.get('message2')
        await self.send(text_data=json.dumps({
            'received_message': message,
            'received_message2': message2,
        }))

        # await self.send(text_data=text_data)


class WsJsonConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive_json(self, content, **kwargs):
        assert isinstance(content, dict)
        self.send_json(content=content)


class WsAsyncJsonConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive_json(self, content, **kwargs):
        assert isinstance(content, dict)
        await self.send_json(content=content)


