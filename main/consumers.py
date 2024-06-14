import json
import asyncio

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from main.models import Player, Inventory, SpecialFeature, Health, Hobby, Room, Speciality, Phobia


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
        feature_id = content['feature_id']  # Change from 'feature_type' to 'feature_id'
        room_name = content['room_name']

        player = await self.get_player(player_id)
        feature = await self.get_feature(feature_id)

        if feature.name == "change_inventory":
            print("I change the inventory")
            new_inventory = await self.change_inventory(player)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'inventory_update',  # Ensure this is being set
                    'player_name': player.player_name,
                    'new_inventory': new_inventory.name
                }
            )
        elif feature.name == "change_health":
            print("I change the health")
            new_health = await self.change_health(player)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'health_update',  # Ensure this is being set
                    'player_name': player.player_name,
                    'new_health': new_health.name
                }
            )
        elif feature.name == "change_speciality":
            print("I change the speciality")
            new_speciality = await self.change_speciality(player)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'speciality_update',  # Ensure this is being set
                    'player_name': player.player_name,
                    'new_speciality': new_speciality.name
                }
            )
        elif feature.name == "change_hobby":
            print("I change the hobby")
            new_hobby = await self.change_hobby(player)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'hobby_update',  # Ensure this is being set
                    'player_name': player.player_name,
                    'new_hobby': new_hobby.name
                }
            )
        elif feature.name == "change_phobias":
            print("I change the phobias")
            new_phobias = await self.change_phobias(player)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'phobias_update',  # Ensure this is being set
                    'player_name': player.player_name,
                    'new_phobias': new_phobias.name
                }
            )
        elif feature.name == "change_human_traits":
            print("I change the human traits")
            new_human_traits = await self.change_human_traits(player)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'human_traits_update',  # Ensure this is being set
                    'player_name': player.player_name,
                    'new_human_traits': new_human_traits.name
                }
            )
        elif feature.name == "change_all_inventories":
            await self.change_inventory_for_all(room_name=room_name)
        elif feature.name == "change_all_hobby":
            await self.change_hobby_for_all(room_name)
        elif feature.name == "change_all_speciality":
            await self.change_speciality_for_all(room_name)
        elif feature.name == "change_all_phobias":
            await self.change_phobias_for_all(room_name)
        # Dummy methods to simulate database operations, replace with actual DB calls

    async def game_message(self, event):
        # Example of handling a generic game message
        await self.send_json({
            'message': event['message'],  # This key should exist
            'player_id': event.get('player_id', ''),
            'new_inventory': event.get('new_inventory', '')
        })

    @database_sync_to_async
    def update_player_inventory(self, player, new_inventory):
        player.inventory = new_inventory
        player.save()

    @database_sync_to_async
    def update_player_hobby(self, player, new_hobby):
        player.hobby = new_hobby
        player.save()

    @database_sync_to_async
    def update_player_speciality(self, player, new_speciality):
        player.speciality = new_speciality
        player.save()

    @database_sync_to_async
    def update_player_phobias(self, player, new_phobia):
        player.phobia = new_phobia
        player.save()

    async def change_phobias_for_all(self, room_name):
        room = await database_sync_to_async(Room.objects.get)(name=room_name)
        players = await database_sync_to_async(list)(room.players.all())
        for player in players:
            new_phobia = await database_sync_to_async(Phobia.objects.order_by('?').first)()
            print(new_phobia)
            print(player.player_name)
            await self.update_player_phobias(player, new_phobia)
            print(player.speciality)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'phobias_update',  # Ensure this is being set
                    'player_name': player.player_name,
                    'new_phobias': new_phobia.name
                }
            )

    async def change_speciality_for_all(self, room_name):
        room = await database_sync_to_async(Room.objects.get)(name=room_name)
        players = await database_sync_to_async(list)(room.players.all())
        for player in players:
            new_speciality = await database_sync_to_async(Speciality.objects.order_by('?').first)()
            print(new_speciality)
            print(player.player_name)
            await self.update_player_speciality(player, new_speciality)
            print(player.speciality)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'speciality_update',  # Ensure this is being set
                    'player_name': player.player_name,
                    'new_speciality': new_speciality.name
                }
            )

    async def change_hobby_for_all(self, room_name):
        room = await database_sync_to_async(Room.objects.get)(name=room_name)
        players = await database_sync_to_async(list)(room.players.all())
        for player in players:
            new_hobby = await database_sync_to_async(Hobby.objects.order_by('?').first)()
            print(new_hobby)
            print(player.player_name)
            await self.update_player_hobby(player, new_hobby)
            print(player.hobby)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'hobby_update',  # Ensure this is being set
                    'player_name': player.player_name,
                    'new_hobby': new_hobby.name
                }
            )

    async def change_inventory_for_all(self, room_name):
        room = await database_sync_to_async(Room.objects.get)(name=room_name)
        players = await database_sync_to_async(list)(room.players.all())
        for player in players:
            new_inventory = await database_sync_to_async(Inventory.objects.order_by('?').first)()
            print(new_inventory)
            print(player.player_name)
            await self.update_player_inventory(player, new_inventory)
            print(player.inventory)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'inventory_update',  # Ensure this is being set
                    'player_name': player.player_name,
                    'new_inventory': new_inventory.name
                }
            )

    @database_sync_to_async
    def get_player(self, player_id):
        return Player.objects.get(pk=player_id)

    @database_sync_to_async
    def get_feature(self, feature_id):
        return SpecialFeature.objects.get(pk=feature_id)

    @database_sync_to_async
    def change_inventory(self, player):
        # Assume you have a method to get a random inventory
        new_inventory = Inventory.objects.order_by('?').first()
        player.inventory = new_inventory
        player.save()
        return new_inventory

    @database_sync_to_async
    def change_health(self, player):
        new_health = Health.objects.order_by('?').first()
        player.health = new_health
        player.save()
        return new_health

    @database_sync_to_async
    def change_speciality(self, player):
        new_speciality = SpecialFeature.objects.order_by('?').first()
        player.speciality = new_speciality
        player.save()
        return new_speciality

    @database_sync_to_async
    def change_hobby(self, player):
        new_hobby = Hobby.objects.order_by('?').first()
        player.hobby = new_hobby
        player.save()
        return new_hobby

    async def inventory_change(self, event):
        # Send the new inventory to all clients in the room
        await self.send_json({
            'type': 'inventory_update',
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
