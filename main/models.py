from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100)
    creatorRoom = models.CharField(max_length=100)
    people = models.ManyToManyField(User)
