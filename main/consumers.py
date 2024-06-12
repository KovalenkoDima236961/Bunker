import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from main.models import Player, Inventory, SpecialFeature


# TODO Проблема полягає в тому, що голосуванні не правильно працює
class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'

        # Приєднання до групи
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Ініціалізація словника для голосів
        self.votes = {}
        # Список гравців, які вже проголосували
        self.voted_players = set()

    async def disconnect(self, close_code):
        # Вихід з групи при роз'єднанні
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        message_type = content.get('message')

        if message_type == 'update':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'update',
                    **content
                }
            )
        elif message_type in ['start_voting', 'vote', 'end_voting']:
            await self.handle_voting(content)
        elif message_type == 'activate_feature':
            await self.activate_feature(content)

    async def activate_feature(self, content):
        player_id = content['player_id']
        feature_id = content['feature_id']

        # Fetch player and feature based on IDs
        player = await self.get_player(player_id)
        feature = await self.get_feature(feature_id)

        if feature.name == "change_inventory":
            new_inventory = await self.change_inventory(player)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'inventory_change',
                    'player_id': player_id,
                    'new_inventory': new_inventory.name
                }
            )
        # Dummy methods to simulate database operations, replace with actual DB calls

    async def get_player(self, player_id):
        # Simulate fetching a player
        return Player(player_id=player_id, inventory=Inventory(name="Old Inventory"))

    async def get_feature(self, feature_id):
        # Simulate fetching a feature
        return SpecialFeature(name="change_inventory")

    async def change_inventory(self, player):
        # Simulate changing inventory
        player.inventory = Inventory(name="New Inventory")
        return player.inventory

    async def inventory_change(self, event):
        # Handle sending the new inventory to all clients
        await self.send_json({
            'type': 'inventory_change',
            'player_id': event['player_id'],
            'new_inventory': event['new_inventory']
        })

    async def handle_voting(self, content):
        message_type = content['message']

        if message_type == 'vote':
            voter = content['voter']
            vote = content['vote']

            # Ініціалізуємо список для кандидата, якщо він ще не існує
            if vote not in self.votes:
                self.votes[vote] = []
            # Додаємо голос, якщо цей виборець ще не голосував за цього кандидата
            if voter not in self.votes[vote]:
                self.votes[vote].append(voter)
                self.voted_players.add(voter)

            # Перевірка, чи всі гравці проголосували
            if len(self.voted_players) >= self.scope["session"]["number_of_players"]:
                # If all have voted, automatically end voting
                await self.end_voting()

        elif message_type == 'start_voting':
            # Ініціалізуємо голосування
            self.votes = {}
            self.voted_players = set()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'start_voting'
                }
            )

        elif message_type == 'end_voting':
            await self.end_voting()

    async def end_voting(self):
        # Надсилання результатів голосування
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message': 'end_voting',
                'votes': {k: len(v) for k, v in self.votes.items()}  # Sending counts instead of voter lists
            }
        )

    async def game_message(self, event):
        # Відправлення повідомлень клієнтам
        await self.send_json(event)
