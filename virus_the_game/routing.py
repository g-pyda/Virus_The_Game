from django.urls import re_path
from .consumers import GameConsumer, LobbyConsumer

websocket_urlpatterns = [
    re_path(r"ws/game/(?P<room_code>\w+)/$", GameConsumer.as_asgi()),
    re_path(r"ws/lobby/(?P<room_code>\w+)/$", LobbyConsumer.as_asgi()),
]
