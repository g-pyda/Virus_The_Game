import json
import aioredis
from channels.generic.websocket import AsyncWebsocketConsumer
from consumer_helpers import (
    get_api_data, post_api_data, delete_api_data, RedisChannelManager
    )
from ..engine.game import Game
from ..engine.player import Player


# ==================== Game Consumer ==================== #


class PlayerConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for individual game players.
    Handles player connections, game actions,
    and direct messaging with other players or host.
    """

    # ------------- connection functions -------------- #
    async def connect(self):
        """
        Establish WebSocket connection for a player.
        Initializes Redis channel manager and registers player's channel name.
        """
        # player authentication
        player = self.scope.get("player")
        if not player:
            await self.close(code=4001)
            return

        self.player = player
        self.nickname = player.nickname

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
        # Initialize Redis manager
        self.redis = await aioredis.create_redis_pool('redis://redis:6379')
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
        await self.send_group_message('player_connected')

    async def disconnect(self, close_code):
        """
        Handle player disconnection.
        Removes player from Redis registry and cleans up Redis connection.
        """
        # Sending the change to the lobby
        await self.send_group_message('player_disconnected')

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
        self.redis.close()
        await self.redis.wait_closed()

        print("Disconnected:", close_code)

    # ----------------- message senders ---------------- #

    async def send_group_message(self, message):
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
                'type': 'group_message',
                'sender': self.player_id,
                'message': message
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


    async def send_message_to_host(self, header, data):
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
                    'type': 'player_message',
                    'header': header,
                    'sender': str(self.player_id),
                    'data': data,
                    }
            )

    # ----------------- message receivers ---------------- #

    async def host_message(self, event):
        """
        Handle incoming message from host.
        Receives direct messages from the host player.
        """
        await self.send(json.dumps({
            'data': event.get('data'),
            'sender': event.get('sender')
        }))

    async def receive(self, message):
        """
        Handle incoming WebSocket messages from the player.
        Parses action type and routes to appropriate handler
        """
        sender = message.get('sender', 'unknown')
        header = message.get('header', '')
        data = message.get('data', {})
        match sender:
            case 'host':
                await self.handle_host_message()
            case 'frontend':
                await self.handle_player_action(header, data)

    async def handle_player_action(self, header, data):
        """
        Handle messages received from the player.
        Routes based on header
        """
        match header:
            case 'connection':
                await self.send_message_to_host(
                    header,
                    {'action': 'add',
                     'nickname': self.nickname}
                    )
            case "turn_end":
                await self.send_message_to_host(
                    header,
                    {'action': 'end-turn'}
                    )
            case 'card_play':
                attempt_info = self.parse_player_action(data)
                await self.send_message_to_host(
                    header,
                    attempt_info
                    )

    async def handle_host_message(self):
        """
        Handle messages received from the host.
        Processes game state updates or commands sent by the host.
        """
        pass  # reaction is handled in frontend

    # ------------ game logic helpers ------------------ #

    def parse_player_action(self, data):
        """
        Route player action to the appropriate handler method.
        Parses action type and extracts relevant parameters.
        """

        action = data.get('action')

        # Route to appropriate handler based on action type
        if action == 'attack':
            attempt_info = self.get_attack_attempt_info(data)
        elif action == 'vaccinate':
            attempt_info = self.get_vaccinate_attempt_info(data)
        elif action == 'heal':
            attempt_info = self.get_heal_attempt_info(data)
        elif action == 'organ':
            attempt_info = self.get_organ_attempt_info(data)
        elif action == 'discard':
            attempt_info = self.get_discard_attempt_info(data)
        elif action == 'special':
            attempt_info = self.get_special_attempt_info(data)
        else:
            attempt_info = {'action': action}

        return attempt_info

    def get_attack_attempt_info(self, data):
        """Extract action info for attack action."""
        return {
            'action': 'attack',
            'card_to_play': data.get('card_id'),
            'target_stack': data.get('target_id'),
            'target_player': data.get('target_id'),
        }

    def get_vaccinate_attempt_info(self, data):
        """Extract action info for vaccinate action."""
        return {
            'action': 'vaccinate',
            'card_to_play': data.get('card_id'),
            'target_stack': data.get('target_id'),
        }

    def get_heal_attempt_info(self, data):
        """Extract action info for heal action."""
        return {
            'action': 'heal',
            'card_to_play': data.get('card_id'),
            'target_stack': data.get('target_id'),
        }

    def get_organ_attempt_info(self, data):
        """Extract action info for organ action."""
        return {
            'action': 'organ',
            'card_to_play': data.get('card_id'),
        }

    def get_discard_attempt_info(self, data):
        """Extract action info for discard action."""
        return {
            'action': 'discard',
            'card_to_play': data.get('card_id'),
        }

    def get_special_attempt_info(self, data):
        """Extract action info for special action based on card type."""
        card_type = data.get('card_type')
        attempt_info = {
            'action': 'special',
            'card_type': card_type,
            'card_to_play': data.get('card_id'),
        }

        if card_type in ["organ swap", "body swap", "theft"]:
            attempt_info.update({
                'target_player': data.get('target_id'),
                'target_stack': data.get('target_stack')
            })

        if card_type in ["organ swap", "body swap"]:
            attempt_info.update({
                'player_stack': data.get('player_stack')
            })

        if card_type == "epidemy":
            attempt_info.update({
                'player_stacks': data.get('player_stacks'),
                'target_stacks': data.get('target_stacks'),
                'target_players': data.get('target_players'),
                'virus_cards': data.get('virus_cards')
            })

        return attempt_info


# =================== Host Consumer ==================== #


class HostConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for game host.
    Manages room channel registry, broadcasts game state to players,
    and handles direct messaging.
    """

    # ------------- connection functions -------------- #

    async def connect(self):
        """
        Establish WebSocket connection for the host.
        Creates and initializes Redis channel manager for the room.
        Initializes the game object.
        """
        # Join room group
        print("Host connecting...")
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"{self.room_code}"

        # Initialize Redis manager
        self.redis = await aioredis.create_redis_pool('redis://redis:6379')
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
        self.game = Game()

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
        self.redis.close()
        await self.redis.wait_closed()

        print("Host disconnected:", close_code)

    # ------------------ message senders ----------------- #

    async def send_group_message(self, message):
        """
        Broadcast a message to all players in the room group.
        Used for game state changes that affect all players.
        """
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'group_message',
                'sender': self.player_id,
                'message': message
            }
        )
        await self.send_direct_message(player_id, payload)

    async def _send_stub_state_to_player(self, player_id: str, request_id=None):
        """
        Temporary state push so you see the protocol works end-to-end.
        Replace later with real engine state.
        """
        await self.send_direct_message(player_id, build_envelope(
            sender="lobby",
            header="turn_state",
            data={"turn": True},
            request_id=request_id
        ))


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

    async def send_message_to_player(self, player_id, header, data):
        """
        Send a direct message to the host.
        Uses Redis to lookup host's channel name for direct delivery.
        """
        host_channel = await self.channel_manager.get_player_channel(
            self.room_code,
            player_id
            )
        if host_channel:
            await self.channel_layer.send(
                host_channel,
                {
                    'type': 'host_message',
                    'header': header,
                    'sender': "host",
                    'data': data,
                    }
            )

    # ----------------- message receivers ---------------- #

    async def player_message(self, event):
        """Handle incoming message from a player."""
        await self.send(json.dumps({
            'action': event.get('action'),
            'data': event.get('data')
            }))

    async def receive(self, message):
        """
        Handle incoming WebSocket messages from the host.
        Routes host commands and game logic decisions.
        """
        sender = message.get('sender', 'unknown')
        header = message.get('header', '')
        data = message.get('data', {})
        match sender:
            case 'player':
                await self.handle_player_message(sender, header, data)
            case 'frontend':
                await self.handle_host_action(header, data)

    async def handle_player_message(self, sender, header, data):
        match header:
            case "connection":
                await self.connect_player(int(sender), data)
            case "card_play":
                await self.players_move(int(sender), data)
            case "turn_end":
                await self.evaluate_turn(int(sender))
            case "all_stacks":
                await self.provide_other_stacks(int(sender))

    # ------------ game logic helpers ------------------ #

    async def connect_player(self, player_id, data):
        try:
            # add the player to the game engine
            self.game.add_player(data.get("nickname"), player_id)
            await self.send_message_to_player(
                    player_id,
                    "attempt",
                    {
                        "status": True,
                        'message': ''
                    })
        except Exception as e:
            await self.send_message_to_player(
                    player_id,
                    "attempt",
                    {
                        "status": False,
                        'message': e.message
                    })

    async def players_move(self, player_id, data):
        try:
            player = self.game.players[player_id]
            attempt = player.attempt_move(data)
            result = self.game.resolve_attempt(player, attempt)
            await self.send_message_to_player(
                    player_id,
                    "attempt",
                    {
                        "status": True,
                        'message': result
                    })
        except Exception as e:
            await self.send_message_to_player(
                    player_id,
                    "attempt",
                    {
                        "status": False,
                        'message': e.message
                    })

    async def evaluate_turn(self, player_id):
        new_player = self.game.next_player()
        for player_id in self.game.player_order:
            await self.send_message_to_player(
                    player_id,
                    "turn_state",
                    {
                        "status": player_id == new_player,
                    })
            await self.send_the_cards(player_id)
            await self.send_the_stacks(player_id)

    async def provide_other_stacks(self, player_id):
        pass

    async def send_the_cards(self, player_id):
        pass

    async def send_the_stacks(self, player_id):
        pass
