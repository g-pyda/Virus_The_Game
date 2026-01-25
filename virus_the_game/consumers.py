import json

import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from .consumer_helpers import (
    get_api_data, post_api_data, delete_api_data, RedisChannelManager
    )
from engine.game import Game
from engine.player import Player

from .consumer_helpers import RedisChannelManager
from .ws_protocol import (
    parse_incoming, parse_payload,
    WsProtocolError, build_attempt,
    build_envelope, build_message
)
from .game_service import GameService

GAME_SERVICE = GameService()

# ==================== Game Consumer ==================== #

class GameConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for individual game players.
    Handles player connections, game actions, and direct messaging with other players or host.
    """

    # ------------- connection functions -------------- #
    async def connect(self):
        """
        Establish WebSocket connection for a player.
        Initializes Redis channel manager and registers player's channel name.
        """
        # Join room group
        print("Connecting...")
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.player_id = self.scope["url_route"]["kwargs"]["player_id"]
        self.room_group_name = f"{self.room_code}"

        # Initialize Redis manager
        self.redis = redis.from_url("redis://redis:6379", decode_responses=True)
        self.channel_manager = RedisChannelManager(self.redis)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
            )

        # Register player's channel name in Redis
        await self.channel_manager.add_player(
            self.room_code, self.player_id, self.channel_name
            )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Handle player disconnection.
        Removes player from Redis registry and notifies host.
        """
        # Notify host about disconnection first
        payload = build_envelope(
            sender=str(self.player_id),
            header="disconnection",
            data={"action": "remove"}
        )
        try:
            await self.send_message_to_host(payload)
        except Exception:
            pass

        try:
            await self.channel_manager.remove_player(self.room_code, self.player_id)
        except Exception:
            pass

        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception:
            pass

        try:
            await self.redis.close()
        except Exception:
            pass

        print("Disconnected:", close_code)

    # ----------------- message handlers ---------------- #

    async def send_message_to_host(self, payload: dict):
        """
        Sends internal channel-layer message to HostConsumer.
        """
        host_channel = await self.channel_manager.get_host_channel(self.room_code)
        if not host_channel:
            # Host not connected yet
            await self.send(build_attempt(False, "Host not connected"))
            return

        await self.channel_layer.send(
            host_channel,
            {
                "type": "host_message",
                "payload": payload,
            }
        )

    async def host_message(self, event):
        """
        Receives internal envelopes from HostConsumer and forwards to browser.
        Browser MUST receive sender="internal".
        """
        payload = event.get("payload")
        if not payload:
            await self.send(build_attempt(False, "Malformed host message (missing payload)"))
            return

        try:
            _sender, header, data, request_id = parse_payload(payload)
        except WsProtocolError as e:
            await self.send(build_attempt(False, f"Malformed host payload: {e}"))
            return

        # Frontend contract: sender="internal"
        await self.send(build_message("internal", header, data, request_id=request_id))

    async def receive(self, text_data=None, bytes_data=None):
        """
        Only accepts frontend envelopes:
        - card_play
        - turn_end
        - connection
        """
        if not text_data:
            return

        try:
            sender, header, data, request_id = parse_incoming(text_data)
        except WsProtocolError as e:
            await self.send(build_attempt(False, str(e)))
            return

        if sender != "frontend":
            await self.send(build_attempt(False, "Invalid sender", request_id=request_id))
            return

        if header == "card_play":
            payload = build_envelope(
                sender=str(self.player_id),
                header="card_play",
                data=data,
                request_id=request_id,
            )
            await self.send_message_to_host(payload)
            return

        if header == "turn_end":
            payload = build_envelope(
                sender=str(self.player_id),
                header="turn_end",
                data={"action": "end_turn"},
                request_id=request_id,
            )
            await self.send_message_to_host(payload)
            return

        if header == "connection":
            payload = build_envelope(
                sender=str(self.player_id),
                header="connection",
                data=data
            )
            await self.send_message_to_host(payload)

        await self.send(build_attempt(False, f"Unknown header: {header}", request_id=request_id))
    
    async def _handle_card_play(self, data: dict, request_id=None):
        # Forward exactly what frontend sent (normalized) to host.
        payload = build_envelope(
            sender=str(self.player_id),
            header="card_play",
            data=data,
            request_id=request_id
        )
        await self.send_message_to_host(payload)

    async def _handle_turn_end(self, data: dict, request_id=None):
        payload = build_envelope(
            sender=str(self.player_id),
            header="turn_end",
            data={"action": "end_turn"},
            request_id=request_id
        )
        await self.send_message_to_host(payload)

    async def lobby_event(self, event):
        """
        Handle group events sent to the room group.
        We forward them to the websocket client so the connection doesn't crash.
        """
        await self.send(json.dumps({
            "type": "lobby_event",
            "receiver": event.get("receiver"),
            "action": event.get("action"),
            "data": event.get("data"),
            "sender_id": event.get("sender_id"),
        }))


# =================== Host Consumer ==================== #

class HostConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for game host.
    Receives player envelopes via internal channel events and applies them to the engine.
    Pushes authoritative state to players using the documented envelope protocol.
    """

    async def connect(self):
        print("Host connecting...")
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"{self.room_code}"

        self.redis = redis.from_url("redis://redis:6379", decode_responses=True)
        self.channel_manager = RedisChannelManager(self.redis)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.channel_manager.set_host(self.room_code, self.channel_name)

        await self.accept()
        print("Host connected to", self.room_group_name)

        GAME_SERVICE.get_or_create(self.room_code)

    async def disconnect(self, close_code):
        try:
            await self.channel_manager.cleanup_room(self.room_code)
        except Exception:
            pass

        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception:
            pass

        try:
            await self.redis.close()
        except Exception:
            pass

    async def receive(self, text_data=None, bytes_data=None):
        """
        Messages from host UI (browser). Optional.
        Accept both:
          - envelope format: {"sender":"frontend","header":"game_start","data":{...}}
        """
        if not text_data:
            return
        
        try:
            sender, header, data, request_id = parse_incoming(text_data)
        except WsProtocolError as e:
            # Host UI should also speak envelope JSON
            await self.send(build_message("internal", "attempt", {"status": False, "message": str(e)}))
            return

        if sender != "frontend":
            await self.send(build_message("internal", "attempt", {"status": False, "message": "Invalid sender"}))
            return

        if header == "game_start":
            started = GAME_SERVICE.start_if_ready(self.room_code)
            await self.send(build_message("internal", "attempt", {"status": True, "message": f"start_game: {started}"}))
            # push state regardless (safe)
            await self._push_state_to_all_players()
            await self._send_internal_to_host_ui(
                "state_change",
                GAME_SERVICE.serialize_host_state_change(self.room_code)
            )
            return

        await self.send(build_message("internal", "attempt", {"status": False, "message": f"Unknown header: {header}"}))

    # ---------------- envelope sending ----------------

    async def _send_to_player(self, player_id: str, payload: dict):
        target_channel = await self.channel_manager.get_player_channel(self.room_code, player_id)
        if not target_channel:
            return
        await self.channel_layer.send(
            target_channel,
            {"type": "host_message", "payload": payload}
        )

    async def _send_attempt_to_player(self, player_id: str, status: bool, message: str = "", request_id=None):
        payload = build_envelope(
            sender="lobby",
            header="attempt",
            data={"status": status, "message": message},
            request_id=request_id,
        )
        await self._send_to_player(player_id, payload)

    async def _push_state_to_player(self, player_id: str, request_id=None):
        pid = int(player_id)

        await self._send_to_player(player_id, build_envelope(
            sender="lobby",
            header="hand_state",
            data=GAME_SERVICE.serialize_hand_state(self.room_code, pid),
            request_id=request_id,
        ))

        await self._send_to_player(player_id, build_envelope(
            sender="lobby",
            header="stacks_state",
            data=GAME_SERVICE.serialize_stacks_state(self.room_code, pid),
            request_id=request_id,
        ))

        await self._send_to_player(player_id, build_envelope(
            sender="lobby",
            header="others_state",
            data=GAME_SERVICE.serialize_others_state(self.room_code, pid),
            request_id=request_id,
        ))

        await self._send_to_player(player_id, build_envelope(
            sender="lobby",
            header="turn_state",
            data=GAME_SERVICE.serialize_turn_state(self.room_code, pid),
            request_id=request_id,
        ))

    async def _push_state_to_all_players(self):
        players = await self.channel_manager.get_all_players(self.room_code)
        for pid in players.keys():
            await self._push_state_to_player(pid)

    async def _send_internal_to_host_ui(self, header: str, data: dict):
        await self.send(build_message("internal", header, data))

    async def host_message(self, event):
        """
        Receives internal message from GameConsumer with event["payload"] (envelope).
        """
        payload = event.get("payload")
        if not payload:
            return

        try:
            player_sender, header, data, request_id = parse_payload(payload)
        except WsProtocolError as e:
            # Can't reliably reply to player if sender unknown; ignore
            return

        handlers = {
            "connection": self._handle_connection,
            "disconnection": self._handle_disconnection,
            "all_stacks": self._handle_all_stacks,
            "card_play": self._handle_card_play,
            "turn_end": self._handle_turn_end,
        }

        handler = handlers.get(header)
        if not handler:
            await self._send_attempt_to_player(player_sender, False, f"Unknown header: {header}", request_id=request_id)
            return

        await handler(player_sender, data, request_id=request_id)

    # ---------------- handlers ----------------

    async def _handle_connection(self, player_id: str, data: dict, request_id=None):
        # Get nickname from player data, fallback to generic if not provided
        nickname = data.get("nickname") or f"Player {player_id}"
        
        try:
            GAME_SERVICE.add_player(self.room_code, int(player_id), name=nickname)
            # Don't auto-start - wait for host signal
        except Exception as e:
            await self._send_attempt_to_player(player_id, False, str(e), request_id=request_id)
            return

        await self._send_internal_to_host_ui("player_join", {
            "player_id": int(player_id),
            "nickname": nickname,
        })

        await self._send_internal_to_host_ui(
            "state_change",
            GAME_SERVICE.serialize_host_state_change(self.room_code)
        )

        await self._send_attempt_to_player(player_id, True, "connected", request_id=request_id)

    async def _handle_disconnection(self, player_id: str, data: dict, request_id=None):
        """
        Handle player disconnection.
        Removes player from game engine and updates frontend.
        """
        try:
            GAME_SERVICE.remove_player(self.room_code, int(player_id))
        except Exception as e:
            # Player might not be in game yet, that's ok
            print(f"Error removing player {player_id}: {e}")

        await self._send_internal_to_host_ui("player_leave", {
            "player_id": int(player_id),
        })

        await self._send_internal_to_host_ui(
            "state_change",
            GAME_SERVICE.serialize_host_state_change(self.room_code)
        )

        print(f"Player {player_id} disconnected from game")

    async def _handle_all_stacks(self, player_id: str, data: dict, request_id=None):
        await self._send_to_player(player_id, build_envelope(
            sender="lobby",
            header="others_state",
            data=GAME_SERVICE.serialize_others_state(self.room_code, int(player_id)),
            request_id=request_id,
        ))

    async def _handle_card_play(self, player_id: str, data: dict, request_id=None):
        try:
            GAME_SERVICE.apply_card_play(self.room_code, int(player_id), data)
        except Exception as e:
            await self._send_attempt_to_player(player_id, False, str(e), request_id=request_id)
            return

        await self._send_attempt_to_player(player_id, True, "", request_id=request_id)
        await self._push_state_to_all_players()
        await self._send_internal_to_host_ui("state_change",
            GAME_SERVICE.serialize_host_state_change(self.room_code)
        )

    async def _handle_turn_end(self, player_id: str, data: dict, request_id=None):
        try:
            GAME_SERVICE.end_turn(self.room_code, int(player_id))
        except Exception as e:
            await self._send_attempt_to_player(player_id, False, str(e), request_id=request_id)
            return

        await self._send_attempt_to_player(player_id, True, "", request_id=request_id)
        await self._push_state_to_all_players()
        await self._send_internal_to_host_ui("turn_end", {})
        await self._send_internal_to_host_ui("state_change",
            GAME_SERVICE.serialize_host_state_change(self.room_code)
        )
