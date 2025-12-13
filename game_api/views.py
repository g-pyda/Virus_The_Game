from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import (
    GameCreateSerializer,
    GameJoinSerializer,
    GameStateSerializer,
)


class GameCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = GameCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO (GAME LOGIC): create a new game
        game_id = 1  # placeholder

        return Response(
            {"game_id": game_id, "message": "Game created"},
            status=status.HTTP_201_CREATED,
        )


class GameJoinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, game_id):
        serializer = GameJoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO (GAME LOGIC): add player to game
        return Response(
            {"message": f"Joined game {game_id}"},
            status=status.HTTP_200_OK,
        )


class GameDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, game_id):
        # TODO (GAME LOGIC): fetch real game state

        data = {
            "game_id": game_id,
            "status": "waiting",
            "players": [],
            "active_player": None,
        }

        serializer = GameStateSerializer(data)
        return Response(serializer.data)
