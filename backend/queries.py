from time import timezone
from models import Player, Game
from django.db import DatabaseError, IntegrityError, OperationalError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# -------- PLAYER QUERIES -------- #


def create_player(nickname: str) -> tuple[Player | None, DatabaseError | None]:
    try:
        player = Player.objects.get(nickname=nickname)
        return player, None
    except IntegrityError:
        return None, DatabaseError("Username already exists")
    except (OperationalError, DatabaseError) as e:
        return None, e


def update_player_score(player_id: int, score: int) -> DatabaseError | None:
    try:
        player = Player.objects.get(id=player_id)
        player.total_score += score
        player.save()
        return None
    except ObjectDoesNotExist:
        return DatabaseError("Player does not exist")
    except (OperationalError, DatabaseError) as e:
        return e


def get_player_id(nickname: str) -> tuple[int | None, DatabaseError | None]:
    try:
        player = Player.objects.get(nickname=nickname)
        return player.id, None
    except ObjectDoesNotExist:
        return None, DatabaseError("Player does not exist")
    except MultipleObjectsReturned:
        return None, DatabaseError(
            "Multiple players with the same nickname found"
            )
    except (OperationalError, DatabaseError) as e:
        return None, e


# -------- GAME QUERIES -------- #

def create_game() -> tuple[Game | None, DatabaseError | None]:
    try:
        game = Game.objects.create()
        return game, None
    except (OperationalError, DatabaseError) as e:
        return None, e


def add_player_to_game(game_id: int, player_id: int) -> DatabaseError | None:
    try:
        game = Game.objects.get(id=game_id)
        game.players.add(player_id)
        game.save()
        return None
    except ObjectDoesNotExist:
        return DatabaseError("Game or Player does not exist")
    except (OperationalError, DatabaseError) as e:
        return e


def finish_game(game_id: int, winner_id: int) -> DatabaseError | None:
    try:
        if not check_if_player_in_game(game_id, winner_id):
            return DatabaseError("Winner is not part of the game")
        game = Game.objects.get(id=game_id)
        game.finished = True
        game.winner_id = winner_id
        game.end_time = timezone.now()
        game.save()
        return None
    except ObjectDoesNotExist:
        return DatabaseError("Game or Player does not exist")
    except (OperationalError, DatabaseError) as e:
        return e


# ------------- HELPERS ------------- #

def check_if_player_in_game(
        game_id: int, player_id: int
        ) -> bool:
    game = Game.objects.get(id=game_id)
    is_in_game = game.players.filter(id=player_id).exists()
    return is_in_game
