from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.apps import apps


@database_sync_to_async
def get_player_for_token(token: str):
    PlayerToken = apps.get_model("backend", "PlayerToken")
    try:
        return PlayerToken.objects.select_related("player").get(value=token).player
    except PlayerToken.DoesNotExist:
        return None


class PlayerTokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        scope["player"] = None
        if token:
            scope["player"] = await get_player_for_token(token)

        return await self.app(scope, receive, send)


def PlayerTokenAuthMiddlewareStack(inner):
    return PlayerTokenAuthMiddleware(inner)
