from django.urls import re_path
from .consumers import GameConsumer, HostConsumer

websocket_urlpatterns = [
    # Player endpoint
    re_path(r"ws/game/(?P<room_code>\w+)/player/(?P<player_id>\w+)/$", GameConsumer.as_asgi()),
    # Host endpoint
    re_path(r"ws/game/(?P<room_code>\w+)/host/$", HostConsumer.as_asgi()),
]
