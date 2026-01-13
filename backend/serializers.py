from rest_framework import serializers
from .models import Game, Player, Card


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "nickname", "total_score"]


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ["id", "card_type", "color", "sub_type"]


class GameSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    winner = PlayerSerializer(source="winner_id", read_only=True)

    class Meta:
        model = Game
        fields = ["id", "finished", "players", "winner", "start_time", "end_time"]
