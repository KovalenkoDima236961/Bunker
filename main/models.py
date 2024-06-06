from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey('Player', null=True, on_delete=models.CASCADE, related_name='created_rooms')

    def __str__(self):
        return self.name


class Player(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    player_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=100, blank=True)
    body_build = models.CharField(max_length=100, blank=True)
    a_human_trait = models.CharField(max_length=100, blank=True)
    speciality = models.CharField(max_length=100, blank=True)
    health = models.CharField(max_length=100, blank=True)
    hobby = models.CharField(max_length=100, blank=True)
    phobia = models.CharField(max_length=100, blank=True)
    inventory = models.CharField(max_length=100, blank=True)
    more_information = models.CharField(max_length=100, blank=True)
    special_feature1 = models.CharField(max_length=100, blank=True)
    special_feature2 = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.player_name
