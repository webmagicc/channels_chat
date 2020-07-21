from rest_framework import serializers

from chat.models import ChatGroup


class ChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ('id', 'name', 'url')
