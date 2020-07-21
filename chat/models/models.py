from django.db import models
from django_lifecycle import LifecycleModelMixin, hook
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class Connection(LifecycleModelMixin, models.Model):
    name = models.CharField(max_length=200, db_index=True, default='')

    @hook('after_update')
    def connection_updated(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            self.name, {
                'type': 'send.message',
                'data': {'message': 'Connection was updated'}
            }
        )


class Group(LifecycleModelMixin, models.Model):
    name = models.CharField(max_length=200, db_index=True, default='')

    def __str__(self):
        return self.name


class GroupMessage(LifecycleModelMixin, models.Model):
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    message = models.TextField(default='')

    @hook('after_create')
    def message_created(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            self.group.name, {
                'type': 'group.message',
                'message': self.message
            }
        )
