import enum
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class Status(enum.Enum):
    OK = 'OK'
    ERROR = 'ERROR'


class ChatBaseConsumer(AsyncJsonWebsocketConsumer):
    STATUS = Status
    ERROR_EVENT = 'websocket.error'

    async def _send_message(self, status, data, event):
        return await self.send_json(content={'status': status, 'data': data, 'event': event})

    async def connect(self):
        await self.accept()
        if 'user' not in self.scope or self.scope['user'].is_anonymous:
            await self._send_message(
                self.STATUS.ERROR.value,
                {'message': 'Please login first'},
                self.ERROR_EVENT
            )
            await self.close()

    async def receive_json(self, content, **kwargs):
        content = await self.parse_content(content)
        if not content:
            await self._send_message(
                self.STATUS.ERROR.value,
                {'detail': 'Wrong message'},
                self.ERROR_EVENT
            )
            return
        event = content['event'].replace('.', '_')
        data = content['data']
        method = getattr(self, f'event_{event}', self.method_undefined)
        await method(data)

    async def parse_content(self, content):
        if (
            isinstance(content, dict) and
            isinstance(content.get('event', None), str) and
            isinstance(content.get('data', None), dict)
        ):
            return content

    async def method_undefined(self, data):
        await self._send_message(
            self.STATUS.ERROR,
            {'detail': 'Unknown event'},
            self.ERROR_EVENT
        )
