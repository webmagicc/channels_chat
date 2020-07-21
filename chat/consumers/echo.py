from channels.generic.websocket import JsonWebsocketConsumer


class EchoConsumer(JsonWebsocketConsumer):
    def receive_json(self, content, **kwargs):
        self.send_json(content=content)
