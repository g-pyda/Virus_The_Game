"""
ASGI config for virus_game_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from virus_the_game.routing import websocket_urlpatterns
from virus_the_game.ws_auth import PlayerTokenAuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virus_the_game.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": PlayerTokenAuthMiddlewareStack(
    URLRouter(websocket_urlpatterns)
    ),
})
