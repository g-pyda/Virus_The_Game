from django.db import IntegrityError, transaction
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Game, Player
from .serializers import GameSerializer


class CreateGameRequestSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=100)


class JoinGameRequestSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=100)


class GameViewSet(viewsets.GenericViewSet):
    queryset = Game.objects.all()

    def create(self, request, *args, **kwargs):
        req = CreateGameRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        nickname = req.validated_data["nickname"]

        try:
            with transaction.atomic():
                game = Game.objects.create()
                player = Player.objects.create(nickname=nickname)
                game.players.add(player)
        except IntegrityError:
            return Response(
                {"detail": "Nickname already exists. Choose a different nickname."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(GameSerializer(game).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        game = self.get_object()

        req = JoinGameRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        nickname = req.validated_data["nickname"]

        try:
            with transaction.atomic():
                player = Player.objects.create(nickname=nickname)
                game.players.add(player)
        except IntegrityError:
            return Response(
                {"detail": "Nickname already exists. Choose a different nickname."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(GameSerializer(game).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def state(self, request, pk=None):
        game = self.get_object()
        return Response(GameSerializer(game).data, status=status.HTTP_200_OK)
