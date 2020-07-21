from django.contrib import admin

from .models import (
    Connection, Group, GroupMessage, GroupParticipant, ChatMessage, ChatGroup
)


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'message')


@admin.register(GroupParticipant)
class GroupParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'user')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'message')


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

