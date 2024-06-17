import json
import asyncio
from collections import Counter

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from main.models import Player, Inventory, SpecialFeature, Health, Hobby, Room, Speciality, Phobia, Bunker, Cataclysm, \
    HumanTrait


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
        elif message_type == 'kick_player':
            player_id = content['player_id']
            player_name = await self.kick_player(player_id)
            if player_name is not None:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'player_kicked',
                        'player_id': player_id,
                        'player_name': player_name,
                    }
                )
        elif message_type == 'end_game':
            room_name = content['room_name']
            success = await self.end_game(room_name)
            if success:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'message': 'end_game',
                    }
                )

    # TODO Check if it works correctly
    @database_sync_to_async
    def end_game(self, room_name):
        try:
            room = Room.objects.get(name=room_name)
            room.delete()
            return True
        except Room.DoesNotExist:
            return False

    @database_sync_to_async
    def kick_player(self, player_id):
        try:
            player = Player.objects.get(pk=player_id)
            player_name = player.player_name
            player.delete()  # This deletes the player record from the database
            return player_name
        except Player.DoesNotExist:
            return None

    async def player_kicked(self, event):
        player_id = event['player_id']
        player_name = event['player_name']
        print(player_name)
        await self.send_json({
            'message': 'you_are_kicked',
            'player_id': player_id,
            'player_name': player_name
        })

    async def activate_feature(self, content):
        player_id = content['player_id']
        feature_id = content['feature_id']  # Change from 'feature_type' to 'feature_id'
        room_name = content['room_name']

        player = await self.get_player(player_id)
        feature = await self.get_feature(feature_id)

        # funcs = {
        #     "change_inventory": (self.change_inventory, "inventory change", 'inventory_update'),
        #     "change_health": self.change_health
        # }
        #
        # ability = funcs.get(feature.name)
        # if ability is None:
        #     pass
        # print(ability[1])
        # res = await (ability[0])(player)
        #
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'game_message',
        #         'message': ability[2],  # Ensure this is being set
        #         'player_name': player.player_name,
        #         'new_inventory': res.name
        #     }
        # )

        # Зробити словник для кожної feature
        # TODO Зробити таке саме і для inventory_change_for_one_person
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
        elif feature.name == "inventory_change_for_one_person":
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
        elif feature.name == "health_change_for_one_person":
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
        elif feature.name == "speciality_change_for_one_person":
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
        elif feature.name == "hobby_change_for_one_person":
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
        elif feature.name == "phobias_change_for_one_person":
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
        elif feature.name == "human_traits_for_one_person":
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
        elif feature.name == "change_bunker":
            new_bunker = await self.change_bunker(room_name)
            if new_bunker:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_message',
                        'message': 'bunker_update',
                        'room_name': room_name,
                        'new_bunker': {
                            'built_years_ago': new_bunker.built_years_ago,
                            'has_hygiene_facilities': new_bunker.has_hygiene_facilities,
                            'location_description': new_bunker.location_description,
                            'capacity': new_bunker.capacity,
                            'size_sqm': new_bunker.size_sqm,
                            'duration_of_stay_years': new_bunker.duration_of_stay_years,
                            'food_supply_years': new_bunker.food_supply_years,
                            'features': [feature.name for feature in new_bunker.features.all()]
                        }
                    }
                )
        elif feature.name == "change_cataclysm":
            # TODO Check if it works
            print("I change cataclysm")
            new_cataclysm = await self.change_cataclysm(room_name)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'cataclysm_update',
                    'room_name': room_name,
                    'new_cataclysm': {
                        'year': new_cataclysm.year,
                        'description': new_cataclysm.description,
                        'how_many_time_do_you_have': new_cataclysm.how_many_time_do_you_have,
                        'remaining_population': new_cataclysm.remaining_population,
                    }
                }
            )
        elif feature.name == "swap_inventory":
            print("I swap inventory")
            current_player_id = content('current_player')
            swap_player_id = content('swap_player')
            inventory_names = await self.swap_player_inventories(current_player_id, swap_player_id)
            if inventory_names[0] is not None:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'message': 'inventory_swap_update',
                        'current_player': current_player_id,
                        'swap_player': swap_player_id,
                        'current_inventory': inventory_names[0],
                        'swap_inventory': inventory_names[1]
                    }
                )
            else:
                print("Failed to swap inventories")
        elif feature.name == "swap_hobby":
            print("I swap hobby")
            current_player_id = content('current_player')
            swap_player_id = content('swap_player')
            hobby_names = await self.swap_player_hobby(current_player_id, swap_player_id)
            if hobby_names[0] is not None:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'message': 'hobby_swap_update',
                        'current_player': current_player_id,
                        'swap_player': swap_player_id,
                        'current_hobby': hobby_names[0],
                        'swap_hobby': hobby_names[1]
                    }
                )
        elif feature.name == "swap_health":
            print("I swap health")
            current_player_id = content('current_player')
            swap_player_id = content('swap_player')
            health_names = await self.swap_player_health(current_player_id, swap_player_id)
            if health_names[0] is not None:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'message': 'health_swap_update',
                        'current_player': current_player_id,
                        'swap_player': swap_player_id,
                        'current_health': health_names[0],
                        'swap_health': health_names[1]
                    }
                )
        elif feature.name == "swap_speciality":
            print("I swap speciality")
            current_player_id = content('current_player')
            swap_player_id = content('swap_player')
            speciality_names = await self.swap_player_speciality(current_player_id, swap_player_id)
            if speciality_names[0] is not None:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'message': 'speciality_swap_update',
                        'current_player': current_player_id,
                        'swap_player': swap_player_id,
                        'current_speciality': speciality_names[0],
                        'swap_speciality': speciality_names[1]
                    }
                )
        elif feature.name == "swap_phobia":
            print("I swap phobia")
            current_player_id = content('current_player')
            swap_player_id = content('swap_player')
            phobia_names = await self.swap_player_phobia(current_player_id, swap_player_id)
            if phobia_names[0] is not None:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'message': 'phobia_swap_update',
                        'current_player': current_player_id,
                        'swap_player': swap_player_id,
                        'current_phobia': phobia_names[0],
                        'swap_phobia': phobia_names[1]
                    }
                )
        elif feature.name == "swap_human_traits":
            print("I swap human traits")
            current_player_id = content('current_player')
            swap_player_id = content('swap_player')
            human_traits_names = await self.swap_player_human_traits(current_player_id, swap_player_id)
            if human_traits_names[0] is not None:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'message': 'human_traits_swap_update',
                        'current_player': current_player_id,
                        'swap_player': swap_player_id,
                        'current_human_traits': human_traits_names[0],
                        'swap_human_traits': human_traits_names[1]
                    }
                )
        # Dummy methods to simulate database operations, replace with actual DB calls

    @database_sync_to_async
    def swap_player_human_traits(self, player_id1, player_id2):
        try:
            player1 = Player.objects.get(pk=player_id1)
            player2 = Player.objects.get(pk=player_id2)
            player1.a_human_trait, player2.a_human_trait = player2.a_human_trait, player1.a_human_trait
            player1.save()
            player2.save()
            return player1.a_human_trait.name, player2.a_human_trait.name
        except Player.DoesNotExist:
            return None, None

    @database_sync_to_async
    def swap_player_phobia(self, player_id1, player_id2):
        try:
            player1 = Player.objects.get(pk=player_id1)
            player2 = Player.objects.get(pk=player_id2)
            player1.phobia, player2.phobia = player2.phobia, player1.phobia
            player1.save()
            player2.save()
            return player1.phobia.name, player2.phobia.name
        except Player.DoesNotExist:
            return None, None

    @database_sync_to_async
    def swap_player_speciality(self, player_id1, player_id2):
        try:
            player1 = Player.objects.get(pk=player_id1)
            player2 = Player.objects.get(pk=player_id2)
            player1.speciality, player2.speciality = player2.speciality, player1.speciality
            player1.save()
            player2.save()
            return player1.speciality.name, player2.speciality.name
        except Player.DoesNotExist:
            return None, None

    @database_sync_to_async
    def swap_player_health(self, player_id1, player_id2):
        try:
            player1 = Player.objects.get(pk=player_id1)
            player2 = Player.objects.get(pk=player_id2)
            player1.health, player2.health = player2.health, player1.health
            player1.save()
            player2.save()
            return player1.health.name, player2.health.name
        except Player.DoesNotExist:
            return None, None

    @database_sync_to_async
    def swap_player_hobby(self, player_id1, player_id2):
        try:
            player1 = Player.objects.get(pk=player_id1)
            player2 = Player.objects.get(pk=player_id2)
            player1.hobby, player2.hobby = player2.hobby, player1.hobby
            player1.save()
            player2.save()
            return player1.hobby.name, player2.hobby.name
        except Player.DoesNotExist:
            return None, None

    @database_sync_to_async
    def swap_player_inventories(self, player_id1, player_id2):
        try:
            player1 = Player.objects.get(pk=player_id1)
            player2 = Player.objects.get(pk=player_id2)
            player1.inventory, player2.inventory = player2.inventory, player1.inventory
            player1.save()
            player2.save()
            return player1.inventory.name, player2.inventory.name
        except Player.DoesNotExist:
            return None, None

    async def game_message(self, event):
        # Example of handling a generic game message
        await self.send_json({
            'message': event['message'],  # This key should exist
            'player_id': event.get('player_id', ''),
            'new_inventory': event.get('new_inventory', '')
        })

    @database_sync_to_async
    def change_bunker(self, room_name):
        try:
            room = Room.objects.get(name=room_name)
            room.bunker = Bunker.objects.order_by('?').first()
            room.save()
            return room.bunker
        except Room.DoesNotExist:
            print("Room not found")
            return None

    @database_sync_to_async
    def change_cataclysm(self, room_name):
        try:
            room = Room.objects.get(name=room_name)
            room.cataclysm = Cataclysm.objects.order_by('?').first()
            room.save()
            return room.cataclysm
        except Room.DoesNotExist:
            print("Room not found")
            return None

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
    def change_human_traits(self, player):
        new_human_traits = HumanTrait.objects.order_by('?').first()
        player.a_human_trait = new_human_traits
        player.save()
        return new_human_traits

    @database_sync_to_async
    def change_phobias(self, player):
        new_phobia = Phobia.objects.order_by('?').first()
        player.phobia = new_phobia
        player.save()
        return new_phobia

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

    @database_sync_to_async
    def get_candidates(self):
        room = Room.objects.get(name=self.room_name)
        return list(room.players.all())

    async def handle_voting(self, content):
        message_type = content['message']

        if message_type == 'vote':
            voter = content['voter']
            vote = content['vote']

            if vote not in self.votes:
                self.votes[vote] = []
            if voter not in self.votes[vote]:
                self.votes[vote].append(voter)
                self.voted_players.add(voter)

            room = await database_sync_to_async(Room.objects.get)(name=self.room_name)
            total_players = await database_sync_to_async(room.players.count)()

            if len(self.voted_players) >= total_players:
                await self.end_voting()

        elif message_type == 'start_voting':
            self.votes = {}
            self.voted_players = set()
            candidates = await self.get_candidates()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'start_voting',
                    'candidates': [{'id': candidate.id, 'name': candidate.player_name} for candidate in candidates]
                }
            )
        elif message_type == 'end_voting':
            await self.end_voting()

    async def end_voting(self):
        results = {candidate: len(votes) for candidate, votes in self.votes.items()}
        max_votes = max(results.values())
        potential_losers = [candidate for candidate, votes in results.items() if votes == max_votes]

        if len(potential_losers) > 1:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "game_message",
                    "message": "tie_voting",
                    "tiedCandidates": [{'id': candidate, 'name': candidate} for candidate in potential_losers]
                }
            )
        else:
            loser = potential_losers[0]
            await self.kick_player(loser)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "voting_ended",
                    "results": results,
                    "loser": loser
                }
            )

    async def voting_ended(self, event):
        results = event['results']
        loser = event['loser']

        await self.send_json({
            'message': 'end_voting',
            'results': results,
            'loser': loser
        })

    async def game_message(self, event):
        # Відправлення повідомлень клієнтам
        await self.send_json(event)
