import json
import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from .consumer_helpers import (
    get_api_data, post_api_data, delete_api_data, RedisChannelManager
    )
from .ws_protocol import parse_incoming, WsProtocolError, build_attempt

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

    async def send_message_to_host(self, action, data):
        """
        Send a direct message to the host.
        Uses Redis to lookup host's channel name for direct delivery.
        """
        host_channel = await self.channel_manager.get_host_channel(
            self.room_code
            )
        if host_channel:
            await self.channel_layer.send(
                host_channel,
                {
                    'type': 'host_message',
                    'action': action,
                    'data': data,
                    'sender_id': self.player_id
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
        Handle incoming message from host.
        Receives direct messages from the host player.
        """
        await self.send(json.dumps({
            'type': 'host_message',
            'action': event['action'],
            'data': event['data'],
            'sender_id': event['sender_id', 'lobby']
        }))

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

    # --------------- tester functions ---------------- #

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            sender, header, data, request_id = parse_incoming(text_data)
        except WsProtocolError as e:
            # Reply to frontend with a consistent "attempt" failure
            await self.send(build_attempt(False, str(e)))
            return

        if sender != "frontend":
            await self.send(build_attempt(False, "Invalid sender"))
            return

        if header == "card_play":
            await self._handle_card_play(data, request_id=request_id)
            return

        if header == "turn_end":
            await self._handle_turn_end(data, request_id=request_id)
            return

        await self.send(build_attempt(False, f"Unknown header: {header}", request_id=request_id))

    async def _handle_card_play(self, data: dict, request_id=None):
        # TEMP: reuse your existing attempt_info construction almost verbatim,
        # but using 'data' instead of 'data = json.loads(text_data)'
        action = data.get("action")
        attempt_info = {"action": action}

        if action in ["attack", "vaccinate", "heal", "organ", "discard", "special"]:
            attempt_info["card_to_play"] = data.get("card_id")

        if action in ["attack", "vaccinate", "heal"]:
            attempt_info["target_stack"] = data.get("target_id")

        if action == "attack":
            attempt_info["target_player"] = data.get("target_id")

        if action == "special":
            card_type = data.get("card_type")
            if card_type in ["organ swap", "body swap", "thieft"]:
                attempt_info.update({
                    "target_player": data.get("target_id"),
                    "target_stack": data.get("target_stack"),
                })
            if card_type in ["organ swap", "body swap"]:
                attempt_info["player_stack"] = data.get("player_stack")
            if card_type == "epidemy":
                attempt_info.update({
                    "player_stacks": data.get("player_stacks"),
                    "target_stacks": data.get("target_stacks"),
                    "target_players": data.get("target_players"),
                    "virus_cards": data.get("virus_cards"),
                })

        await self.send_message_to_host("player_move", attempt_info)


    async def _handle_turn_end(self, data: dict, request_id=None):
        # normalize payload for host
        await self.send_message_to_host("turn_end", {"action": "end_turn"})


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
    Manages room channel registry, broadcasts game state to players, and handles direct messaging.
    """
    
    async def connect(self):
        """
        Establish WebSocket connection for the host.
        Creates and initializes Redis channel manager for the room.
        """
        # Join room group
        print("Host connecting...")
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"{self.room_code}"

        # Initialize Redis manager
        self.redis = redis.from_url("redis://redis:6379", decode_responses=True)
        self.channel_manager = RedisChannelManager(self.redis)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Register host's channel name in Redis
        await self.channel_manager.set_host(self.room_code, self.channel_name)

        await self.accept()
        print("Host connected to", self.room_group_name)
        print(f"Room Manager created in Redis for room: {self.room_code}")

        # Creating the game instance in the host consumer
        # self.game = Game()

    async def disconnect(self, close_code):
        """
        Handle host disconnection.
        Cleans up all room data in Redis and closes Redis connection.
        """
        # Clean up room data in Redis
        await self.channel_manager.cleanup_room(self.room_code)

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Close Redis connection
        await self.redis.close()


        print("Host disconnected:", close_code)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handle incoming WebSocket messages from the host UI (browser).
        """
        if not text_data:
            return

        data = json.loads(text_data)
        action = data.get("action")

        match action:
            case "start_game":
                print("Game started by host.")
            case _:
                print(f"Unknown host action: {action}")


    async def send_direct_message(self, target_player_id, action, data):
        """
        Send a direct message to a specific player from the host.
        Uses Redis to lookup target player's channel name for direct delivery.
        """
        target_channel = await self.channel_manager.get_player_channel(
            self.room_code, target_player_id
        )
        if target_channel:
            await self.channel_layer.send(
                target_channel,
                {
                    'type': 'host_message',
                    'action': action,
                    'data': data,
                    "sender_id": "lobby",

                }
            )

    async def broadcast_to_all_players(self, action, data):
        """
        Send a message to all players in the room.
        Broadcasts game state or commands to all
        connected players simultaneously.
        """
        players = await self.channel_manager.get_all_players(self.room_code)
        for player_id, channel_name in players.items():
            await self.channel_layer.send(
                channel_name,
                {
                    'type': 'host_message',
                    'action': action,
                    'data': data,
                    "sender_id": "lobby",

                }
            )

    async def host_direct_message(self, event):
        """Handle incoming message from a player."""
        await self.send(json.dumps({
            'type': 'host_direct_message',
            'action': event['action'],
            'data': event['data']
        }))

    async def player_connected(self, event):
        """Handle player connection event."""
        data = event['data']
        await self.send(json.dumps({
            'type': 'player_connected',
            'data': data
        }))

    async def player_disconnected(self, event):
        """Handle player disconnection event."""
        data = event['data']
        await self.send(json.dumps({
            'type': 'player_disconnected',
            'data': data
        }))

    async def card_used(self, event):
        data = event['data']
        await self.send(json.dumps({
            'type': 'card_used',
            'data': data
        }))

    async def card_discarded(self, event):
        data = event['data']
        await self.send(json.dumps({
            'type': 'card_discarded',
            'data': data
        }))

    async def turn_ended(self, event):
        data = event['data']
        await self.send(json.dumps({
            'type': 'turn_ended',
            'data': data
        }))

    async def lobby_event(self, event):
    # Only host should act on these; receiver can be used for filtering if needed
        await self.send(json.dumps({
            "type": "lobby_event",
            "receiver": event["receiver"],
            "action": event["action"],
            "data": event["data"],
            "sender_id": event.get("sender_id"),
        }))

    async def host_message(self, event):
        """
        Handle incoming direct message from a player (sent via channel_layer.send).
        """
        action = event.get("action")
        data = event.get("data", {})
        sender_id = str(event.get("sender_id"))

        handlers = {
        "player_move": self._handle_player_move,
        "turn_end": self._handle_turn_end_from_player,
        }

        handler = handlers.get(action)
        if not handler:
            await self.send(json.dumps({
                "type": "host_message",
                "action": event.get("action"),
                "data": event.get("data"),
                "sender_id": event.get("sender_id", "lobby"),
            }))
            return

        await handler(sender_id, data)

    async def _handle_player_move(self, sender_id: str, data: dict):
        # TEMP: just acknowledge back to that player so you confirm the round trip
        await self.send_direct_message(
            target_player_id=sender_id,
            action="attempt",
            data={"status": True, "message": "received player_move"}
        )

    async def _handle_turn_end_from_player(self, sender_id: str, data: dict):
        await self.send_direct_message(
            target_player_id=sender_id,
            action="attempt",
            data={"status": True, "message": "received turn_end"}
        )
