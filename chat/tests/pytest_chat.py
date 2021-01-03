import pytest
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.test import Client
from channels.testing.websocket import WebsocketCommunicator

from channels_chat.routing import application


User = get_user_model()


@database_sync_to_async
def create_user(username, email, password):
    user = User.objects.create_user(
        username=username, email=email, password=password
    )
    return user


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def pytest_chat():
    client1 = Client()
    client2 = Client()
    user1 = await create_user('test1', 'test1@gmail.com', '1qaz2wsx3edc')
    user2 = await create_user('test2', 'test2@gmail.com', '1qaz2wsx3edc')
    client1.force_login(user=user1)
    client2.force_login(user=user2)
    communicator = WebsocketCommunicator(
        application=application,
        path='/ws/chat/',
        headers=[
            (
                b'cookie',
                f"sessionid={client1.cookies['sessionid'].value}".encode('ascii')
            )
        ]
    )
    connected, _ = await communicator.connect()
    assert connected, "Connection fail"

    await communicator.send_json_to(
        {"event": "group.create", "data": {"name": "Group 1"}}
    )
    message = await communicator.receive_json_from()
    assert message['status'] == 'OK', message
    assert message['event'] == 'group.create', message
    assert message['data']['name'] == 'Group 1', message
    group_url = message['data']['url']

    await communicator.send_json_to(
        {"event": "groups.list", "data": {}}
    )
    message = await communicator.receive_json_from()
    assert message['event'] == 'groups.list', message
    assert len(message['data']) == 1, message

    await communicator.disconnect()

    group_communicator = WebsocketCommunicator(
        application=application,
        path=group_url,
        headers=[
            (
                b'cookie',
                f"sessionid={client1.cookies['sessionid'].value}".encode('ascii')
            )
        ]
    )
    connected, _ = await group_communicator.connect()
    assert connected, "Connection fail"

    chat_communicator = WebsocketCommunicator(
        application=application,
        path='/ws/chat/',
        headers=[
            (
                b'cookie',
                f"sessionid={client2.cookies['sessionid'].value}".encode('ascii')
            )
        ]
    )
    connected, _ = await chat_communicator.connect()
    assert connected, "Connection fail"

    await group_communicator.send_json_to(
        {"event": "add.participants", "data": {"user_ids": [user2.id]}}
    )
    message = await group_communicator.receive_json_from()
    assert message['event'] == 'participant.list', message

    message = await chat_communicator.receive_json_from()
    assert message['event'] == 'groups.list', message

    await chat_communicator.disconnect()

    group_communicator2 = WebsocketCommunicator(
        application=application,
        path=group_url,
        headers=[
            (
                b'cookie',
                f"sessionid={client2.cookies['sessionid'].value}".encode('ascii')
            )
        ]
    )

    connected, _ = await group_communicator2.connect()
    assert connected, "Connection fail"

    await group_communicator.send_json_to(
        {"event": "post.message", "data": {"message": "hello"}}
    )

    message = await group_communicator.receive_json_from()
    assert message['event'] == 'post.list', message
    assert message['data'][0]["message"] == 'hello', message

    message = await group_communicator2.receive_json_from()
    assert message['event'] == 'post.list', message
    assert message['data'][0]["message"] == 'hello', message

    await group_communicator.disconnect()
    await group_communicator2.disconnect()



