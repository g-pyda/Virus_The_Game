import json
from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        player = self.scope.get("player")
        if not player:
            await self.close(code=4001)
            return

        self.player = player

        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"{self.room_code}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print("Player connected to", self.room_group_name)
        print("Connected.")

    async def disconnect(self, close_code):
        print("Disconnected:", close_code)

    async def receive(self, text_data):
        data = json.loads(text_data)
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


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        player = self.scope.get("player")
        if not player:
            await self.close(code=4001)
            return

        self.player = player

        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"{self.room_code}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("Player connected to lobby", self.room_group_name)

    async def disconnect(self, close_code):
        print("Disconnected from lobby:", close_code)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "lobby_message",
                "message": message,
            }
        )

    async def lobby_message(self, event):
        await self.send(json.dumps({
            "type": "lobby",
            "message": event["message"],
        }))