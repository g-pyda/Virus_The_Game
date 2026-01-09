import json
from channels.generic.websocket import AsyncWebsocketConsumer
from consumer_helpers import get_api_data, post_api_data, delete_api_data


class GameConsumer(AsyncWebsocketConsumer):
    # ------------- connection functions -------------- #
    async def connect(self):
        # Join room group
        print("Connecting...")
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.player_id = self.scope["url_route"]["kwargs"]["player_id"]
        self.room_group_name = f"{self.room_code}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print("Player connected to", self.room_group_name)
        print("Connected.")

        # Notify lobby of new connection
        await self.send_message(
            'lobby', 'player_connected',
            {'player_id': self.player_id})

    async def disconnect(self, close_code):
        # Sending the change to the lobby
        await self.send_message(
            'lobby', 'player_disconnected',
            {'player_id': self.player_id})

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("Disconnected:", close_code)

    # ----------------- message handlers ---------------- #

    async def send_message(self, receiver, action, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'receiver': receiver,
                'action': action,
                'data': data
            }
        )

    # ----------------- game functions ---------------- #

    async def use_card(self, card_id, target_id, player_id):
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
        # Sending the change to the game logic handler
        await self.send_message(
            'lobby', 'card_discarded',
            {
                'card_id': card_id,
                'player_id': player_id
            }
        )
        print(f"Player {player_id} discarded card {card_id}")

    async def end_turn(self, player_id):
        # Sending the change to the game logic handler
        await self.send_message(
            'lobby', 'turn_ended',
            {'player_id': player_id})
        
        print(f"Player {player_id} ended their turn")

    # --------------- tester functions ---------------- #

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'use_card':
            await self.use_card(
                data.get('card_id'),
                data.get('target_id'),
                data.get('player_id')
                )
        elif action == 'discard_card':
            await self.discard_card(
                data.get('card_id'),
                data.get('player_id')
                )
        elif action == 'end_turn':
            await self.end_turn(
                data.get('player_id')
                )

        message = data.get('message')

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        await self.send(json.dumps({
            'type': 'chat',
            'message': message
        }))


class HostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join room group
        print("Host connecting...")
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"{self.room_code}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("Host connected to", self.room_group_name)

        # Creating the game instance in the host consumer
        # self.game = Game()

    async def disconnect(self, close_code):
        print("Host disconnected:", close_code)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        # Handle lobby-specific actions here

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