from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Any, List

from engine.game import Game
from engine.card import Card, SpecialCard, Stack
from .attempt_translator import ws_card_play_to_attempt_info



class GameService:
    """
    One Game instance per room_code. This is intentionally in-memory for now.
    Later you can back it by Redis/DB if needed.
    """
    def __init__(self):
        self._games: Dict[str, Game] = {}

    def get_or_create(self, room_code: str) -> Game:
        if room_code not in self._games:
            self._games[room_code] = Game()
        return self._games[room_code]

    # ---- player lifecycle ----

    def add_player(self, room_code: str, player_id: int, name: str | None = None) -> Dict[str, Any]:
        game = self.get_or_create(room_code)
        if name is None:
            name = f"Player {player_id}"
        return game.add_player(name=name, player_id=player_id)

    def start_if_ready(self, room_code: str) -> None:
        """
        For now: start automatically once there are >=2 players and deck not initialized.
        Adjust to your lobby flow later.
        """
        game = self.get_or_create(room_code)
        if len(game.players) >= 2 and not game.deck.cards and not game.deck.discard_pile:
            game.start_game()

    # ---- serialization to websocket protocol ----

    def serialize_hand_state(self, room_code: str, player_id: int) -> Dict[str, Any]:
        game = self.get_or_create(room_code)
        player = game.players[player_id]
        return {
            "cards": [self._serialize_card(c) for c in player.on_hand]
        }

    def serialize_stacks_state(self, room_code: str, player_id: int) -> Dict[str, Any]:
        game = self.get_or_create(room_code)
        player = game.players[player_id]
        return {
            "stacks": [self._serialize_stack(s) for s in player.laid_out]
        }

    def serialize_others_state(self, room_code: str, player_id: int) -> Dict[str, Any]:
        game = self.get_or_create(room_code)
        others = []
        for other_id in game.player_order:
            if other_id == player_id:
                continue
            p = game.players[other_id]
            others.append({
                "player_id": p.id,
                "player_name": p.name,
                "stacks": [self._serialize_stack(s) for s in p.laid_out],
            })
        return {"players": others}

    def serialize_turn_state(self, room_code: str, player_id: int) -> Dict[str, Any]:
        game = self.get_or_create(room_code)
        current_player_id = game.player_order[game.index_of_current_player] if game.player_order else None
        return {"turn": (current_player_id == player_id)}

    # ---- helpers ----

    def _serialize_card(self, c: Card | SpecialCard) -> Dict[str, Any]:
        if isinstance(c, SpecialCard):
            return {"card_id": c.id, "color": "special", "value": 100, "card_type": c.card_type}
        return {"card_id": c.id, "color": c.color, "value": c.value, "card_type": ""}

    def _serialize_stack(self, s: Stack) -> Dict[str, Any]:
        # Protocol expects stack_id, color, value (you can choose stack_value or status)
        return {"stack_id": s.id, "color": s.color, "value": s.stack_value}
    
    def apply_card_play(self, room_code: str, player_id: int, ws_data: dict) -> dict:
        """
        Apply a card_play to the engine. Returns a result dict suitable for logging/debugging.
        """
        game = self.get_or_create(room_code)

        if player_id not in game.players:
            raise ValueError(f"Player {player_id} not in game")

        player = game.players[player_id]

        attempt_info = ws_card_play_to_attempt_info(game, player_id, ws_data)
        attempt = player.attempt_move(attempt_info)
        result = game.resolve_attempt(player, attempt)

        # After a successful attempt you usually draw a card or advance turn depending on rules.
        # Keep this explicit and implement according to your design.
        return result

    def end_turn(self, room_code: str, player_id: int) -> None:
        game = self.get_or_create(room_code)

        # Basic rule: only current player can end turn
        current = game.player_order[game.index_of_current_player] if game.player_order else None
        if current is not None and current != player_id:
            raise ValueError("Not your turn")

        # Advance turn
        game.next_player()

def start_if_ready(self, room_code: str) -> bool:
    """
    Start the game once there are >=2 players and the deck is not initialized.
    Returns True if the game was started in this call.
    """
    game = self.get_or_create(room_code)

    # already started (deck initialized) -> do nothing
    if game.deck.cards or game.deck.discard_pile:
        return False

    if len(game.players) >= 2:
        game.start_game()
        return True

    return False
