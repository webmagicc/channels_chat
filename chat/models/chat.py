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

    @hook('after_create')
    def created(self):
        if not self.user:
            return
        from chat.serializers import ChatGroupSerializer
        qs = ChatGroup.objects.filter(groupparticipant__user=self.user)
        data = {
            "type": "groups.list",
            "data": ChatGroupSerializer(qs, many=True).data,
            "event": "group.list"
        }
        channel_layers = get_channel_layer()
        group_name = self.get_group_name(self.user.id)
        async_to_sync(channel_layers.group_send)(
            group_name, data
        )


class ChatMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    participant = models.ForeignKey(GroupParticipant, on_delete=models.CASCADE)
    message = models.TextField()

    def __str__(self):
        return self.message
