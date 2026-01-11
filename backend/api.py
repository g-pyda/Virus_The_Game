from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Game, Player
from .serializers import GameSerializer, PlayerSerializer

def ok(**data):
    return Response({"status": "success", **data}, status=status.HTTP_200_OK)

def created(**data):
    return Response({"status": "success", **data}, status=status.HTTP_201_CREATED)

def err(message: str, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"status": "error", "message": message}, status=status_code)


class CreateGameRequestSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=100)


class JoinGameRequestSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=100, required=False, allow_blank=False)
    player_name = serializers.CharField(max_length=100, required=False, allow_blank=False)

    def validate(self, attrs):
        nickname = attrs.get("nickname") or attrs.get("player_name")
        if not nickname:
            raise serializers.ValidationError("player_name is required")
        attrs["nickname"] = nickname
        return attrs


class GameViewSet(viewsets.GenericViewSet):
    queryset = Game.objects.all()

    def create(self, request, *args, **kwargs):
        req = CreateGameRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        nickname = req.validated_data["nickname"]

        try:
            with transaction.atomic():
                game = Game.objects.create()
                player, _ = Player.objects.get_or_create(nickname=nickname)
                game.players.add(player)
        except IntegrityError:
            return err("Database error")

        return created(game_id=game.id, game=GameSerializer(game).data)

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        game = self.get_object()

        req = JoinGameRequestSerializer(data=request.data)
        if not req.is_valid():
            return err("player_name is required")

        nickname = req.validated_data["nickname"]

        with transaction.atomic():
            player, _ = Player.objects.get_or_create(nickname=nickname)
            game.players.add(player)

        return ok(player_id=player.id, game_id=game.id, game=GameSerializer(game).data)

    @action(detail=True, methods=["get"])
    def state(self, request, pk=None):
        game = self.get_object()
        return ok(game_id=game.id, game=GameSerializer(game).data)

    @action(detail=True, methods=["delete"])
    def remove_player(self, request, pk=None):
        game = self.get_object()
        player_id = request.query_params.get("player_id") or request.data.get("player_id")
        if not player_id:
            return err("player_id is required")

        try:
            player = Player.objects.get(id=int(player_id))
        except (ValueError, Player.DoesNotExist):
            return err("Player not found", status.HTTP_404_NOT_FOUND)

        game.players.remove(player)
        return ok(game_id=game.id)

    @action(detail=True, methods=["patch"])
    def finish(self, request, pk=None):
        game = self.get_object()

        winner_id = request.data.get("winner_id")
        if winner_id is not None:
            try:
                winner = Player.objects.get(id=int(winner_id))
            except (ValueError, Player.DoesNotExist):
                return err("Winner not found", status.HTTP_404_NOT_FOUND)
            game.winner_id = winner

        game.finished = True
        game.end_time = timezone.now()
        game.save()

        return ok(message="Game finished", game_id=game.id)


class PlayerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Player.objects.all().order_by("-total_score", "nickname")
    serializer_class = PlayerSerializer
