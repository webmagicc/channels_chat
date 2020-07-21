from channels.generic.websocket import JsonWebsocketConsumer


class ScopeExample(JsonWebsocketConsumer):
    def receive_json(self, content, **kwargs):
        print(">>>>>>  SCOPE  <<<<<<<")
        for k in self.scope.keys():
            if k != 'headers':
                print()
                print(k, " >> ", self.scope[k])
        print(">>>>>>  HEADERS  <<<<<<<")
        for header in self.scope['headers']:
            print()
            print(header[0], " >> ", header[1])
