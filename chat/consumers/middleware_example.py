from channels.generic.websocket import JsonWebsocketConsumer


class MiddlewareExampleConsumer(JsonWebsocketConsumer):
    def receive_json(self, content, **kwargs):
        for k in self.scope.keys():
            if k != 'headers':
                print()
                print(k, " >> ", self.scope[k])
