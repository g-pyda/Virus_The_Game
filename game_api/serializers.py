from rest_framework import serializers


class GameCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class GameJoinSerializer(serializers.Serializer):
    player_name = serializers.CharField(max_length=100)


class GameStateSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    status = serializers.CharField()
    players = serializers.ListField(child=serializers.CharField())
    active_player = serializers.CharField(allow_null=True)
