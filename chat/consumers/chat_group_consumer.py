from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from chat.consumers.chat_base_consumer import ChatBaseConsumer
from chat.models import GroupParticipant, ChatMessage, ChatGroup
from chat.serializers import UserSerializer, ChatMessageSerializer


User = get_user_model()


class ChatGroupConsumer(ChatBaseConsumer):

    async def connect(self):
        await super().connect()
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group = await self.get_group_by_id(self.group_id)
        self.group_name = ChatGroup.get_group_name(self.group_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await super().disconnect(code)

    async def event_add_participants(self, data):
        user_ids = data.get('user_ids', [])
        if user_ids:
            await self.add_participants(user_ids)

    async def event_remove_participants(self, data):
        user_ids = data.get('user_ids', [])
        if user_ids:
            await self.remove_participants(user_ids)

    async def event_post_message(self, data):
        message = data.get('message', None)
        await self.create_message(message)

    async def event_user_list(self, data):
        data = await self.get_users_list()
        await self._send_message(
            self.STATUS.OK.value,
            data,
            'user.list'
        )

    async def event_participant_list(self, data):
        participants = await self.get_participants()
        await self._send_message(
            self.STATUS.OK.value,
            participants,
            'participant.list'
        )

    async def event_post_list(self, data):
        data = await self.get_post_list()
        await self._send_message(
            self.STATUS.OK.value,
            data,
            'post.list'
        )

    async def layers_method(self, event):
        await self._send_message(
            self.STATUS.OK.value,
            event['data'],
            event['event']
        )

    # database methods

    @database_sync_to_async
    def get_group_by_id(self, group_id):
        return ChatGroup.objects.get(id=group_id)

    @database_sync_to_async
    def get_users_list(self):
        user_ids = list(GroupParticipant.objects.filter(
            group=self.group
        ).values_list('user_id', flat=True))
        qs = User.objects.all().exclude(id__in=user_ids)
        return UserSerializer(qs, many=True).data

    @database_sync_to_async
    def add_participants(self, user_ids):
        for user_id in user_ids:
            GroupParticipant.objects.get_or_create(
                group=self.group, user_id=user_id
            )

    @database_sync_to_async
    def remove_participants(self, user_ids):
        GroupParticipant.objects.filter(
            group=self.group, user_id__in=user_ids
        ).delete()
        GroupParticipant.send_update_participant_list_by_group_id(self.group_id)

    @database_sync_to_async
    def create_message(self, message):
        participant = GroupParticipant.objects.filter(
            user=self.scope['user'], group=self.group
        ).first()
        if participant:
            ChatMessage.objects.create(
                group=self.group, participant=participant,
                message=message
            )

    @database_sync_to_async
    def get_participants(self):
        qs = User.objects.filter(groupparticipant__group=self.group)
        return UserSerializer(qs, many=True).data

    @database_sync_to_async
    def get_post_list(self):
        qs = ChatMessage.objects.filter(group=self.group).order_by('id')
        return ChatMessageSerializer(qs, many=True).data


