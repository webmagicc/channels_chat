from channels.db import database_sync_to_async

from .chat_base_consumer import ChatBaseConsumer
from chat.models import ChatGroup, GroupParticipant
from chat.serializers import ChatGroupSerializer


class ChatGroupListConsumer(ChatBaseConsumer):
    async def connect(self):
        await super().connect()
        self.group_name = GroupParticipant.get_group_name(self.scope['user'].id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await super().disconnect(code)

    async def event_groups_list(self, data):
        group_list = await self.get_groups_list()
        await self._send_message(
            self.STATUS.OK.value, group_list, 'groups.list'
        )

    async def event_group_create(self, data):
        name = data.get('name', None)
        if not name:
            await self._send_message(
                self.STATUS.ERROR.value, {'detail': 'Group name is missing'},
                'group.create'
            )
        group = await self.create_group(name)
        await self._send_message(
            self.STATUS.OK.value, group, 'group.create'
        )

    @database_sync_to_async
    def get_groups_list(self):
        qs = ChatGroup.objects.filter(
            groupparticipant__user=self.scope['user']
        )
        return ChatGroupSerializer(qs, many=True).data

    @database_sync_to_async
    def create_group(self, name):
        group = ChatGroup.objects.create(name=name)
        GroupParticipant.objects.create(
            group=group, user=self.scope['user']
        )
        return ChatGroupSerializer(group).data

    # Channel Layers methods

    async def groups_list(self, event):
        await self._send_message(
            self.STATUS.OK.value,
            event['data'],
            event['event']
        )
