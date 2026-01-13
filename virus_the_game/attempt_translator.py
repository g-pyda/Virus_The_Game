from __future__ import annotations

from typing import Any, Dict, List, Optional

from engine.card import SpecialCard
from engine.game import Game


def _require_int(data: Dict[str, Any], key: str) -> int:
    val = data.get(key)
    if val is None:
        raise ValueError(f"Missing required field '{key}'")
    if not isinstance(val, int):
        raise ValueError(f"Field '{key}' must be int")
    return val


def _optional_int(data: Dict[str, Any], key: str) -> Optional[int]:
    val = data.get(key)
    if val is None:
        return None
    if not isinstance(val, int):
        raise ValueError(f"Field '{key}' must be int")
    return val


def _optional_int_list(data: Dict[str, Any], key: str) -> Optional[List[int]]:
    val = data.get(key)
    if val is None:
        return None
    if not isinstance(val, list) or any(not isinstance(x, int) for x in val):
        raise ValueError(f"Field '{key}' must be a list[int]")
    return val


def _get_card_type_from_hand(game: Game, player_id: int, card_id: int) -> Optional[str]:
    """
    If the chosen card is a SpecialCard, infer its card_type from the engine state.
    """
    player = game.players[player_id]
    card = next((c for c in player.on_hand if getattr(c, "id", None) == card_id), None)
    if card is None:
        raise ValueError(f"Card {card_id} not found in player {player_id} hand")
    if isinstance(card, SpecialCard):
        return card.card_type
    return None


def ws_card_play_to_attempt_info(
    game: Game,
    player_id: int,
    ws_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Translate websocket 'card_play' message data (WEBSOCKET_COMMUNICATION.md) into
    attempt_info expected by engine.Player.attempt_move().

    Supported ws_data fields (from doc):
      action, card_id, target_id, target_stack, player_stack,
      target_stacks, player_stacks, target_players, virus_cards

    Engine attempt_move expects keys such as:
      card_id, target_player_id, target_stack_id, stack_id,
      discard_cards_ids, virus_cards_ids, player_stacks_ids, target_stacks_ids, target_players_ids
    """
    if not isinstance(ws_data, dict):
        raise ValueError("card_play data must be an object")

    action = ws_data.get("action")
    if not isinstance(action, str) or not action:
        raise ValueError("Missing/invalid 'action' in card_play.data")

    attempt_info: Dict[str, Any] = {"action": action}

    # Common: card_id is required for most actions except discard (depending on your UI)
    card_id = ws_data.get("card_id")
    if card_id is not None and not isinstance(card_id, int):
        raise ValueError("'card_id' must be int")

    # --- Simple actions ---

    if action in ("attack", "vaccinate", "heal", "organ"):
        if card_id is None:
            raise ValueError(f"'card_id' is required for action '{action}'")
        attempt_info["card_id"] = card_id

    if action == "organ":
        # nothing else required
        return attempt_info

    if action in ("vaccinate", "heal"):
        # target stack can be provided as target_stack OR (legacy) target_id
        target_stack_id = _optional_int(ws_data, "target_stack")
        if target_stack_id is None:
            target_stack_id = _require_int(ws_data, "target_id")
        attempt_info["target_stack_id"] = target_stack_id
        return attempt_info

    if action == "attack":
        # attack requires BOTH target player and target stack
        target_player_id = _require_int(ws_data, "target_id")
        target_stack_id = _optional_int(ws_data, "target_stack")
        if target_stack_id is None:
            raise ValueError("Missing required field 'target_stack' for action 'attack'")
        attempt_info["target_player_id"] = target_player_id
        attempt_info["target_stack_id"] = target_stack_id
        return attempt_info

    # --- Discard ---
    if action == "discard":
        # The protocol doc doesn’t specify discard payload clearly.
        # Accept a few common variants to keep frontend flexible.
        discard_ids = (
            _optional_int_list(ws_data, "discard_cards_ids")
            or _optional_int_list(ws_data, "discard_cards")
            or _optional_int_list(ws_data, "cards")
        )
        if not discard_ids:
            raise ValueError(
                "Discard requires a list of card ids in one of: "
                "'discard_cards_ids', 'discard_cards', or 'cards'"
            )
        attempt_info["discard_cards_ids"] = discard_ids
        return attempt_info

    # --- Special ---
    if action == "special":
        if card_id is None:
            raise ValueError("'card_id' is required for action 'special'")
        attempt_info["card_id"] = card_id

        # Determine special type:
        # prefer ws_data['card_type'] if provided, else infer from engine hand
        card_type = ws_data.get("card_type")
        if card_type is not None and not isinstance(card_type, str):
            raise ValueError("'card_type' must be string")

        if not card_type:
            card_type = _get_card_type_from_hand(game, player_id, card_id)

        if not card_type:
            raise ValueError("Could not determine special card_type (not provided and not inferable)")

        # For engine.Player.attempt_move(), "special" means:
        # - if the card is special: attempt_move will branch based on card_to_play.card_type
        # - it expects certain keys depending on card_type
        # We supply those keys in the names attempt_move expects.

        if card_type in ("organ swap", "body swap"):
            # needs: stack_id (my stack), target_player_id, target_stack_id
            attempt_info["stack_id"] = _require_int(ws_data, "player_stack")
            attempt_info["target_player_id"] = _require_int(ws_data, "target_id")
            attempt_info["target_stack_id"] = _require_int(ws_data, "target_stack")
            return attempt_info

        if card_type == "thieft":
            attempt_info["target_player_id"] = _require_int(ws_data, "target_id")
            attempt_info["target_stack_id"] = _require_int(ws_data, "target_stack")
            return attempt_info

        if card_type == "latex glove":
            # no extra fields required
            return attempt_info

        if card_type == "epidemy":
            virus_cards_ids = _optional_int_list(ws_data, "virus_cards")
            player_stacks_ids = _optional_int_list(ws_data, "player_stacks")
            target_stacks_ids = _optional_int_list(ws_data, "target_stacks")
            target_players_ids = _optional_int_list(ws_data, "target_players")

            if not virus_cards_ids:
                raise ValueError("epidemy requires 'virus_cards' list[int]")
            if not player_stacks_ids:
                raise ValueError("epidemy requires 'player_stacks' list[int]")
            if not target_stacks_ids:
                raise ValueError("epidemy requires 'target_stacks' list[int]")
            if not target_players_ids:
                raise ValueError("epidemy requires 'target_players' list[int]")

            n = len(virus_cards_ids)
            if not (len(player_stacks_ids) == len(target_stacks_ids) == len(target_players_ids) == n):
                raise ValueError("epidemy lists must have equal length: virus_cards/player_stacks/target_stacks/target_players")

            attempt_info["virus_cards_ids"] = virus_cards_ids
            attempt_info["player_stacks_ids"] = player_stacks_ids
            attempt_info["target_stacks_ids"] = target_stacks_ids
            attempt_info["target_players_ids"] = target_players_ids
            return attempt_info

        raise ValueError(f"Unknown special card_type: {card_type}")

    raise ValueError(f"Unknown action: {action}")
