from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100)
    creator_room = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    people = models.ManyToManyField(User, on_delete=models.CASCADE, related_name='rooms')

    def __str__(self):
        return self.name


class Player(models.Model):
    # Add to Room
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    body_build = models.CharField(max_length=100)
    a_human_trait = models.CharField(max_length=100)
    speciality = models.CharField(max_length=100)
    health = models.CharField(max_length=100)
    hobby = models.CharField(max_length=100)
    phobia = models.CharField(max_length=100)
    inventory = models.CharField(max_length=100)
    more_information = models.CharField(max_length=100)
    special_feature1 = models.CharField(max_length=100)
    special_feature2 = models.CharField(max_length=100)

    def __str__(self):
        return self.name
