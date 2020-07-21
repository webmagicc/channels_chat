from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import CookieMiddleware, SessionMiddlewareStack

from chat.routing import websocket_urls
from chat.middleware import MyMiddlewareStack, SimpleMiddlewareStack


application = ProtocolTypeRouter({
   'websocket': MyMiddlewareStack(URLRouter(websocket_urls)),
})
