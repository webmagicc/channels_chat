from django.conf.urls import url

from chat.consumers import EchoConsumer
from chat.consumers.examples import BaseAsyncConsumer, BaseSyncConsumer, WsConsumer, WsAsyncConsumer, \
    WsJsonConsumer, WsAsyncJsonConsumer
from chat.consumers.scope import ScopeExample
from chat.consumers.send import SendConsumer
from chat.consumers.group import GroupSendConsumer, GroupSendSyncConsumer
from chat.consumers.middleware_example import MiddlewareExampleConsumer
from chat.consumers.middlevare_session import MiddlewareSessionConsumer, AsyncMiddlewareSessionConsumer
from chat.consumers.middleware_auth import MiddlewareAuthConsumer, AsyncMiddlewareAuthConsumer
from chat.consumers.my_middleware import MyMiddlewareConsumer
from chat.consumers.chat_group_list_consumer import ChatGroupListConsumer
from chat.consumers.chat_group_consumer import ChatGroupConsumer

websocket_urls = [
    url(r'^ws/chat/(?P<group_id>\d+)/$', ChatGroupConsumer),
    url(r'^ws/chat/$', ChatGroupListConsumer),
    url(r'^ws/my_middleware/$', MyMiddlewareConsumer),
    url(r'^ws/middleware/auth/$', MiddlewareAuthConsumer),
    url(r'^ws/middleware/session/$', AsyncMiddlewareSessionConsumer),
    url(r'^ws/middleware/$', MiddlewareExampleConsumer),
    url(r'^ws/group/(?P<group_name>\w+)/$', GroupSendConsumer),
    url(r'^ws/group_sync/(?P<group_name>\w+)/$', GroupSendSyncConsumer),
    url(r'^ws/send/$', SendConsumer),
    url(r'^ws/scope/(?P<my_var>\w+)/', ScopeExample),
    url(r'^ws/echo/$', EchoConsumer),
    url(r'^ws/base/$', BaseSyncConsumer),
    url(r'^ws/base_async/$', BaseAsyncConsumer),
    url(r'^ws/ws/$', WsConsumer),
    url(r'^ws/ws_async/$', WsAsyncConsumer),
    url(r'^ws/ws_json/$', WsJsonConsumer),
    url(r'^ws/ws_json_async/$', WsAsyncJsonConsumer),
]
