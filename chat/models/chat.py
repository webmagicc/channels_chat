from django.db import models
from django.contrib.auth import get_user_model
from django_lifecycle import LifecycleModelMixin, hook
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


User = get_user_model()


class ChatGroup(models.Model):
    name = models.CharField(max_length=100, default='')

    @classmethod
    def get_group_name(cls, group_id):
        return f"group_{group_id}"

    @property
    def url(self):
        return f"/ws/chat/{self.id}/"

    def __str__(self):
        return self.name


class GroupParticipant(LifecycleModelMixin, models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @classmethod
    def get_group_name(cls, user_id):
        return f"user_{user_id}_groups"

    def __str__(self):
        return self.user.email

    @classmethod
    def _send_channel_layers_event(cls, group_name, json_data, type_name, event_name):
        data = {
            "type": type_name,
            "data": json_data,
            "event": event_name
        }
        channel_layers = get_channel_layer()
        async_to_sync(channel_layers.group_send)(
            group_name, data
        )

    def change_groups_list(self):
        from chat.serializers import ChatGroupSerializer
        qs = ChatGroup.objects.filter(groupparticipant__user=self.user)
        json_data = ChatGroupSerializer(qs, many=True).data
        group_name = self.get_group_name(self.user.id)
        self._send_channel_layers_event(
            group_name, json_data, 'groups.list', 'groups.list'
        )

    def change_participants_list(self):
        self.send_update_participant_list_by_group_id(self.group.id)

    @classmethod
    def send_update_participant_list_by_group_id(cls, group_id):
        from chat.serializers import UserSerializer
        qs = User.objects.filter(groupparticipant__group_id=group_id)
        json_data = UserSerializer(qs, many=True).data
        group_name = ChatGroup.get_group_name(group_id)
        cls._send_channel_layers_event(
            group_name, json_data, 'layers.method', 'participant.list'
        )

    @hook('after_create')
    def created(self):
        self.change_groups_list()
        self.change_participants_list()

    @hook('after_delete')
    def deleted(self):
        self.change_groups_list()
        self.change_participants_list()


class ChatMessage(LifecycleModelMixin, models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    participant = models.ForeignKey(GroupParticipant, on_delete=models.CASCADE)
    message = models.TextField()

    @hook('after_create')
    def created(self):
        if not self.group:
            return None
        from chat.serializers import ChatMessageSerializer
        qs = ChatMessage.objects.filter(group=self.group).order_by('id')
        data = {
            "type": "layers.method",
            "data": ChatMessageSerializer(qs, many=True).data,
            "event": "post.list"
        }
        channel_layers = get_channel_layer()
        group_name = ChatGroup.get_group_name(self.group_id)
        async_to_sync(channel_layers.group_send)(
            group_name, data
        )

    def __str__(self):
        return self.message
