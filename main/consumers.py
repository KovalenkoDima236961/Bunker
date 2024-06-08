import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'game_%s' % self.room_name

        # Initialize votes
        self.votes = {}

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

        if message == 'update':
            info_type = text_data_json['info_type']
            info_value = text_data_json['info_value']
            player_name = text_data_json['player_name']

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'update',
                    'info_type': info_type,
                    'info_value': info_value,
                    'player_name': player_name
                }
            )

        elif message == 'start_voting':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'start_voting',
                }
            )

        elif message == 'end_voting':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'end_voting',
                    'votes': self.votes
                }
            )

        elif message == 'vote':
            vote = text_data_json['vote']
            voter = text_data_json['voter']

            if vote not in self.votes:
                self.votes[vote] = []

            if voter not in self.votes[vote]:
                self.votes[vote].append(voter)

    async def game_message(self, event):
        message = event['message']

        if message == 'update':
            info_type = event['info_type']
            info_value = event['info_value']
            player_name = event['player_name']

            await self.send(text_data=json.dumps({
                'message': message,
                'info_type': info_type,
                'info_value': info_value,
                'player_name': player_name
            }))

        elif message in ['start_voting', 'end_voting']:
            if message == 'end_voting':
                votes = event['votes']
                await self.send(text_data=json.dumps({
                    'message': message,
                    'votes': votes
                }))
            else:
                await self.send(text_data=json.dumps({
                    'message': message,
                }))