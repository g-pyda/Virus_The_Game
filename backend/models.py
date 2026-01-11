from django.db import models
import secrets


class Game(models.Model):
    finished = models.BooleanField(default=False)
    players = models.ManyToManyField("Player", related_name="games")
    winner = models.ForeignKey(
        "Player",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="won_games",
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

# # - to be deleted
# class GameState(models.Model):
#     game_id = models.ForeignKey(Game, on_delete=models.RESTRICT)
#     player_id = models.ForeignKey('Player', on_delete=models.RESTRICT)
#     card_id = models.ForeignKey('Card', on_delete=models.RESTRICT)
#     card_state = models.CharField(max_length=100)
#     timestamp = models.DateTimeField(auto_now_add=True)


class Player(models.Model):
    nickname = models.CharField(max_length=100, unique=True)
    total_score = models.IntegerField(default=0)

class PlayerToken(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name="token")
    value = models.CharField(max_length=64, unique=True)

    @staticmethod
    def generate(player):
        token, _ = PlayerToken.objects.get_or_create(
            player=player,
            defaults={"value": secrets.token_hex(32)}
        )
        return token

# # - to be deleted
# class Card(models.Model):
#     card_type = models.CharField(max_length=100)
#     color = models.CharField(max_length=50)
#     sub_type = models.CharField(max_length=100, null=True, blank=True)

# Card Class, could be changed later for game logic
class Card(models.Model):
    card_type = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    sub_type = models.CharField(max_length=100, null=True, blank=True)