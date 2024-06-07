from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey('Player', null=True, on_delete=models.CASCADE, related_name='created_rooms')
    bunker = models.ForeignKey('Bunker', on_delete=models.SET_NULL, null=True, blank=True)
    cataclysm = models.ForeignKey('Cataclysm', on_delete=models.SET_NULL, null=True, blank=True)
    is_game_started = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Player(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    player_name = models.CharField(max_length=100)
    gender = models.ForeignKey('Gender', on_delete=models.SET_NULL, null=True, blank=True)
    body_build = models.ForeignKey('BodyBuild', on_delete=models.SET_NULL, null=True, blank=True)
    a_human_trait = models.ForeignKey('HumanTrait', on_delete=models.SET_NULL, null=True, blank=True)
    speciality = models.ForeignKey('Speciality', on_delete=models.SET_NULL, null=True, blank=True)
    health = models.ForeignKey('Health', on_delete=models.SET_NULL, null=True, blank=True)
    hobby = models.ForeignKey('Hobby', on_delete=models.SET_NULL, null=True, blank=True)
    phobia = models.ForeignKey('Phobia', on_delete=models.SET_NULL, null=True, blank=True)
    inventory = models.ForeignKey('Inventory', on_delete=models.SET_NULL, null=True, blank=True)
    more_information = models.ForeignKey('MoreInformation', on_delete=models.SET_NULL, null=True, blank=True)
    special_feature1 = models.ForeignKey('SpecialFeature', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='special_feature1_players')
    special_feature2 = models.ForeignKey('SpecialFeature', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='special_feature2_players')

    is_gender_open = models.BooleanField(default=False)
    is_body_build_open = models.BooleanField(default=False)
    is_human_trait_open = models.BooleanField(default=False)
    is_speciality_open = models.BooleanField(default=False)
    is_health_open = models.BooleanField(default=False)
    is_hobby_open = models.BooleanField(default=False)
    is_phobia_open = models.BooleanField(default=False)
    is_inventory_open = models.BooleanField(default=False)
    is_more_information_open = models.BooleanField(default=False)
    is_special_feature1_open = models.BooleanField(default=False)
    is_special_feature2_open = models.BooleanField(default=False)

    def __str__(self):
        return self.player_name


class Gender(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class BodyBuild(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class HumanTrait(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Speciality(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Health(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Hobby(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Phobia(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class MoreInformation(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class SpecialFeature(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class BunkerFeature(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Bunker(models.Model):
    built_years_ago = models.PositiveIntegerField()
    has_hygiene_facilities = models.BooleanField()
    location_description = models.CharField(max_length=255)
    size_sqm = models.PositiveIntegerField()
    duration_of_stay_years = models.PositiveIntegerField()
    food_supply_years = models.PositiveIntegerField()
    features = models.ManyToManyField(BunkerFeature)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f'Bunker ({self.size_sqm} sqm, {self.capacity} capacity)'


class Cataclysm(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    description = models.CharField(max_length=400)
    how_many_time_do_you_have = models.CharField(max_length=100)
    remaining_population = models.CharField(max_length=150)

    def __str__(self):
        return f"Cataclysm {self.year}: {self.description[:50]}..."
