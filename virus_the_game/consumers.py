import json

import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer

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
        
        # Notify host using documented envelope format (if host already connected)
        payload = build_envelope(
            sender=str(self.player_id),
            header="connection",
            data={"action": "add"}
        )
        await self.send_message_to_host(payload)


        print("Player connected to", self.room_group_name)
        players = await self.channel_manager.get_all_players(self.room_code)
        print(f"Room Manager - Room: {self.room_code}, Players: {players}")
        print("Connected.")

        # Notify lobby of new connection
        await self.send_message(
            'lobby', 'player_connected',
            {'player_id': self.player_id})

    async def disconnect(self, close_code):
        """
        Handle player disconnection.
        Removes player from Redis registry and cleans up Redis connection.
        """
        # Sending the change to the lobby
        await self.send_message(
            'lobby', 'player_disconnected',
            {'player_id': self.player_id})

        # Remove player from Redis
        await self.channel_manager.remove_player(
            self.room_code, self.player_id
            )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Close Redis connection
        await self.redis.close()

        print("Disconnected:", close_code)

    # ----------------- message handlers ---------------- #

    async def send_message(self, receiver, action, data):
        """
        Broadcast a message to all players in the room group.
        Used for game state changes that affect all players.
        """
        await self.channel_layer.group_send(
        self.room_group_name,
        {
            "type": "lobby_event",
            "receiver": receiver,
            "action": action,
            "data": data,
            "sender_id": self.player_id,
        }
    )

    async def send_direct_message(self, target_player_id, action, data):
        """
        Send a direct message to a specific player.
        Uses Redis to lookup target player's channel name for direct delivery.
        """
        target_channel = await self.channel_manager.get_player_channel(
            self.room_code, target_player_id
        )
        if target_channel:
            await self.channel_layer.send(
                target_channel,
                {
                    'type': 'direct_message',
                    'action': action,
                    'data': data,
                    'sender_id': self.player_id
                }
            )

    async def send_message_to_host(self, payload: dict):
        """
        Send a message envelope to the host (internal channel_layer message).
        """
        host_channel = await self.channel_manager.get_host_channel(self.room_code)
        if host_channel:
            await self.channel_layer.send(
                host_channel,
                {
                    "type": "host_message",
                    "payload": payload,
                }
            )


    async def direct_message(self, event):
        """
        Handle incoming direct message from another player.
        Receives and forwards player-to-player messages.
        """
        await self.send(json.dumps({
            'type': 'direct_message',
            'action': event['action'],
            'data': event['data'],
            'sender_id': event['sender_id']
        }))

    async def host_message(self, event):
        """
        Incoming internal message from host. Expect event["payload"] as an envelope.
        Forward envelope to frontend as JSON string.
        """
        payload = event.get("payload")
        if not payload:
            # Fallback: keep old behavior if someone sends action/data
            await self.send(json.dumps({
                "sender": "lobby",
                "header": "attempt",
                "data": {"status": False, "message": "Malformed host message (missing payload)"}
            }))
            return

        try:
            sender, header, data, request_id = parse_payload(payload)
        except WsProtocolError as e:
            await self.send(build_attempt(False, f"Malformed host payload: {e}"))
            return

        # Forward exactly in documented format
        await self.send(build_message(sender, header, data, request_id=request_id))



    # ----------------- game functions ---------------- #

    async def use_card(self, card_id, target_id, player_id):
        """
        Process card usage action by a player.
        Sends card usage event to the game host for validation and processing.
        """
        # Sending the change to the lobby
        await self.send_message(
            'lobby', 'card_used',
            {
                'card_id': card_id,
                'target_id': target_id,
                'player_id': player_id
            }
        )

        # If successfull, broadcast the change to all players
        print(f"Player {player_id} used card {card_id}")
        # If failed, communicate for the player

    async def discard_card(self, card_id, player_id):
        """
        Process card discard action by a player.
        Sends card discard event to the game host for recording.
        """
        await self.send_message(
            'lobby', 'card_discarded',
            {
                'card_id': card_id,
                'player_id': player_id
            }
        )
        print(f"Player {player_id} discarded card {card_id}")

    async def end_turn(self, player_id):
        """
        Process end turn action by a player.
        Notifies the host that the player has finished their turn.
        """
        await self.send_message(
            'lobby', 'turn_ended',
            {'player_id': player_id})
    
        print(f"Player {player_id} ended their turn")

    async def receive(self, text_data=None, bytes_data=None):
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

        handlers = {
            "card_play": self._handle_card_play,
            "turn_end": self._handle_turn_end,
        }

        handler = handlers.get(header)
        if not handler:
            await self.send(build_attempt(False, f"Unknown header: {header}", request_id=request_id))
            return

        await handler(data, request_id=request_id)


    # async def _handle_card_play(self, data: dict, request_id=None):
    #     # TEMP: reuse your existing attempt_info construction almost verbatim,
    #     # but using 'data' instead of 'data = json.loads(text_data)'
    #     action = data.get("action")
    #     attempt_info = {"action": action}

    #     if action in ["attack", "vaccinate", "heal", "organ", "discard", "special"]:
    #         attempt_info["card_to_play"] = data.get("card_id")

    #     if action in ["attack", "vaccinate", "heal"]:
    #         attempt_info["target_stack"] = data.get("target_id")

    #     if action == "attack":
    #         attempt_info["target_player"] = data.get("target_id")

    #     if action == "special":
    #         card_type = data.get("card_type")
    #         if card_type in ["organ swap", "body swap", "thieft"]:
    #             attempt_info.update({
    #                 "target_player": data.get("target_id"),
    #                 "target_stack": data.get("target_stack"),
    #             })
    #         if card_type in ["organ swap", "body swap"]:
    #             attempt_info["player_stack"] = data.get("player_stack")
    #         if card_type == "epidemy":
    #             attempt_info.update({
    #                 "player_stacks": data.get("player_stacks"),
    #                 "target_stacks": data.get("target_stacks"),
    #                 "target_players": data.get("target_players"),
    #                 "virus_cards": data.get("virus_cards"),
    #             })

    #     await self.send_message_to_host("player_move", attempt_info)
    
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


    async def chat_message(self, event):
        """
        Handle and forward chat messages.
        Broadcasts chat messages to the connected player.
        """

        await self.send(json.dumps({
        "type": "chat",
        "message": event["message"],
    }))
    
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

    async def disconnect(self, close_code):
        await self.channel_manager.cleanup_room(self.room_code)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.redis.close()
        print("Host disconnected:", close_code)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Messages from host UI (browser). Optional.
        Keep this minimal; gameplay comes from players via host_message().
        """
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(json.dumps({"type": "error", "message": "Invalid JSON from host UI"}))
            return

        action = data.get("action")
        if action == "start_game":
            # Optional: call GAME_SERVICE.start_if_ready(...) or explicit start
            await self.send(json.dumps({"type": "info", "message": "start_game not implemented yet"}))
        else:
            await self.send(json.dumps({"type": "info", "message": f"Unknown host action: {action}"}))

    # ---------------- envelope sending ----------------

    async def send_direct_message(self, target_player_id: str, payload: dict):
        """
        Send an envelope directly to a player (internal channel event).
        """
        target_channel = await self.channel_manager.get_player_channel(self.room_code, target_player_id)
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
            request_id=request_id
        )
        await self.send_direct_message(player_id, payload)

    async def _push_state_to_player(self, player_id: str, request_id=None):
        pid = int(player_id)

        await self.send_direct_message(player_id, build_envelope(
            sender="lobby",
            header="hand_state",
            data=GAME_SERVICE.serialize_hand_state(self.room_code, pid),
            request_id=request_id
        ))

        await self.send_direct_message(player_id, build_envelope(
            sender="lobby",
            header="stacks_state",
            data=GAME_SERVICE.serialize_stacks_state(self.room_code, pid),
            request_id=request_id
        ))

        await self.send_direct_message(player_id, build_envelope(
            sender="lobby",
            header="others_state",
            data=GAME_SERVICE.serialize_others_state(self.room_code, pid),
            request_id=request_id
        ))

        await self.send_direct_message(player_id, build_envelope(
            sender="lobby",
            header="turn_state",
            data=GAME_SERVICE.serialize_turn_state(self.room_code, pid),
            request_id=request_id
        ))

    async def _push_state_to_all_players(self):
        players = await self.channel_manager.get_all_players(self.room_code)
        for pid in players.keys():
            await self._push_state_to_player(pid)

    # ---------------- inbound from players ----------------

    async def lobby_event(self, event):
        """
        Optional: if you still broadcast room-level events, they will come here.
        Keep only if you use group_send(type="lobby_event") for host UI visibility.
        """
        await self.send(json.dumps({
            "type": "lobby_event",
            "receiver": event.get("receiver"),
            "action": event.get("action"),
            "data": event.get("data"),
            "sender_id": event.get("sender_id"),
        }))

    async def host_message(self, event):
        """
        Internal message from a player consumer.
        Requires event["payload"] as an envelope.
        """
        payload = event.get("payload")
        if not payload:
            await self.send(json.dumps({
                "type": "error",
                "message": "Malformed player message: missing payload"
            }))
            return

        try:
            sender, header, data, request_id = parse_payload(payload)
        except WsProtocolError as e:
            await self.send(json.dumps({"type": "error", "message": f"Malformed player payload: {e}"}))
            return

        handlers = {
            "connection": self._handle_connection,
            "all_stacks": self._handle_all_stacks,
            "card_play": self._handle_card_play,
            "turn_end": self._handle_turn_end,
        }

        handler = handlers.get(header)
        if not handler:
            await self._send_attempt_to_player(sender, False, f"Unknown header: {header}", request_id=request_id)
            return

        await handler(sender, data, request_id=request_id)

    # ---------------- handlers ----------------

    async def _handle_connection(self, player_id: str, data: dict, request_id=None):
        try:
            GAME_SERVICE.add_player(self.room_code, int(player_id))
            started_now = GAME_SERVICE.start_if_ready(self.room_code)
        except Exception as e:
            await self._send_attempt_to_player(player_id, False, str(e), request_id=request_id)
            return

        await self._send_attempt_to_player(player_id, True, "connected", request_id=request_id)

        # If the game started now (2nd player joined), everybody needs fresh state.
        if started_now:
            await self._push_state_to_all_players()
        else:
            await self._push_state_to_player(player_id, request_id=request_id)


    async def _handle_all_stacks(self, player_id: str, data: dict, request_id=None):
        # Send only others_state; frontend can request this when needed
        await self.send_direct_message(player_id, build_envelope(
            sender="lobby",
            header="others_state",
            data=GAME_SERVICE.serialize_others_state(self.room_code, int(player_id)),
            request_id=request_id
        ))

    async def _handle_card_play(self, player_id: str, data: dict, request_id=None):
        try:
            GAME_SERVICE.apply_card_play(self.room_code, int(player_id), data)
        except Exception as e:
            await self._send_attempt_to_player(player_id, False, str(e), request_id=request_id)
            return

        await self._send_attempt_to_player(player_id, True, "", request_id=request_id)
        await self._push_state_to_all_players()

    async def _handle_turn_end(self, player_id: str, data: dict, request_id=None):
        try:
            # implement in service if you want: advance turn, draw card, etc.
            GAME_SERVICE.end_turn(self.room_code, int(player_id))
        except Exception as e:
            await self._send_attempt_to_player(player_id, False, str(e), request_id=request_id)
            return

        await self._send_attempt_to_player(player_id, True, "", request_id=request_id)
        await self._push_state_to_all_players()
