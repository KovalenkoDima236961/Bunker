from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100)
    creator_room = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    people = models.ManyToManyField(User, related_name='rooms')

    def __str__(self):
        return self.name

