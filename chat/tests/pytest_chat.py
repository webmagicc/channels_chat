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

