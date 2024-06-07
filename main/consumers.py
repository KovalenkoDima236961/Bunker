import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'game_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        info_type = text_data_json['info_type']
        info_value = text_data_json['info_value']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message': message,
                'info_type': info_type,
                'info_value': info_value
            }
        )

    async def game_message(self, event):
        message = event['message']
        info_type = event['info_type']
        info_value = event['info_value']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'info_type': info_type,
            'info_value': info_value
        }))