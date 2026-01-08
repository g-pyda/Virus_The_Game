import json
from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
    # ------------- connection functions -------------- #
    async def connect(self):
        print("Connecting...")
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"{self.room_code}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("Player connected to", self.room_group_name)
        print("Connected.")

    async def disconnect(self, close_code):
        print("Disconnected:", close_code)

    # ----------------- game functions ---------------- #

    async def use_card(self, card_id, target_id, player_id):
        # Sending the change to the game logic handler
        # --> Here the request is validated and processed

        # If successfull, broadcast the change to all players
        print(f"Player {player_id} used card {card_id}")
        # If failed, communicate for the player

    async def discard_card(self, card_id, player_id):
        # Sending the change to the game logic handler
        # --> Here the request is validated and processed
        print(f"Player {player_id} discarded card {card_id}")

    async def end_turn(self, player_id):
        # Sending the next turn signal to the players
        print(f"Player {player_id} ended their turn")

    # --------------- tester functions ---------------- #

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'use_card':
            await self.use_card(
                data['card_id'], data['target_id'], data['player_id']
                )
        elif action == 'discard_card':
            await self.discard_card(data['card_id'], data['player_id'])
        elif action == 'end_turn':
            await self.end_turn(data['player_id'])

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
