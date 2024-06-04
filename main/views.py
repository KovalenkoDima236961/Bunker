from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import random
from main.models import Room


def generate_random_name(length=10):
    all_char = 'qwertyuioplkjhgfdsazxcvbnm1234567890'
    return ''.join(random.choice(all_char) for _ in range(length))


def index(request):
    return render(request, 'index.html')


def game(request):
    if request.method == 'POST':
        username = request.POST['username']
        creator = User.objects.create_user(username=username)

        name = generate_random_name()
        while Room.objects.filter(name=name).exists():
            name = generate_random_name()

        room = Room.objects.create(name=name, creator_room=creator)
        room.people.add(creator)

        request.session['username'] = username

        return redirect('game_room', room_id=name)

    return render(request, 'index.html')


def game_room(request, room_id):
    room = get_object_or_404(Room, name=room_id)
    username = request.session.get('username')
    if not username:
        messages.error(request, 'Please enter a username')
        return redirect('index')
    user = get_object_or_404(User, username=username)
    is_creator = room.creator_room == user
    return render(request, 'game_room.html', {'room': room, 'username': username, 'is_creator': is_creator})


def join_room(request):
    if request.method == 'POST':
        room_name = request.POST['room_name']
        username = request.POST['username']

        if Room.objects.filter(name=room_name).exists():
            room = Room.objects.get(name=room_name)

            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_user(username=username)

            room.people.add(user)

            request.session['username'] = username

            return redirect('game_room', room_id=room_name)
        else:
            messages.error(request, 'Room does not exist')
            return redirect('index')

    return redirect('index')


def number_of_people(request, room_id):
    room = get_object_or_404(Room, name=room_id)
    players = list(room.people.values('username'))
    return JsonResponse({'count': room.people.count(), 'players': players})
