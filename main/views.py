from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import random
from main.models import Room, Player


def generate_random_name(length=10):
    all_char = 'qwertyuioplkjhgfdsazxcvbnm1234567890'
    return ''.join(random.choice(all_char) for _ in range(length))


def index(request):
    return render(request, 'index.html')


def game(request):
    if request.method == 'POST':
        player_name = request.POST['player_name']

        name = generate_random_name()
        while Room.objects.filter(name=name).exists():
            name = generate_random_name()

        room = Room.objects.create(name=name)

        creator = Player.objects.create(room=room, player_name=player_name)
        room.creator = creator
        room.save()

        request.session['player_name'] = player_name

        return redirect('game_room', room_id=room.name)

    return render(request, 'index.html')


def game_room(request, room_id):
    room = get_object_or_404(Room, name=room_id)
    player_name = request.session.get('player_name')
    if not player_name:
        messages.error(request, 'Please enter a player name')
        return redirect('index')
    is_creator = room.creator.player_name == player_name
    return render(request, 'game_room.html', {'room': room, 'player_name': player_name, 'is_creator': is_creator})


def join_room(request):
    if request.method == 'POST':
        room_name = request.POST['room_name']
        player_name = request.POST['player_name']

        if Room.objects.filter(name=room_name).exists():
            room = Room.objects.get(name=room_name)

            if room.players.count() == 15:
                messages.info(request, 'The room is full')
                return redirect('index')

            if room.players.filter(player_name=player_name).exists():
                messages.error(request, 'Player name already exists in the room')
                return redirect('index')

            Player.objects.create(room=room, player_name=player_name)

            request.session['player_name'] = player_name

            return redirect('game_room', room_id=room.name)
        else:
            messages.error(request, 'Room does not exist')
            return redirect('index')

    return redirect('index')


def number_of_people(request, room_id):
    room = get_object_or_404(Room, name=room_id)
    players = list(room.players.values('player_name'))
    return JsonResponse({'count': room.players.count(), 'players': players})


def close_room(request, room_id):
    room = get_object_or_404(Room, name=room_id)
    player_name = request.session.get('player_name')

    if player_name == room.creator.player_name:
        room.delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)


def exit_room(request, room_id):
    room = get_object_or_404(Room, name=room_id)
    player_name = request.session.get('player_name')

    if not player_name:
        return JsonResponse({'status': 'error', 'message': 'Player not found in session'}, status=400)

    player = get_object_or_404(Player, room=room, player_name=player_name)
    player.delete()

    if 'player_name' in request.session:
        del request.session['player_name']

    return JsonResponse({'status': 'success'})


def remove_player(request, room_id):
    room = get_object_or_404(Room, name=room_id)
    player_id = request.POST.get('player_id')
    player = get_object_or_404(Player, player_name=player_id, room=room)

    player_name = request.session.get('player_name')
    if room.creator.player_name == player_name:
        player.delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)


def check_player_in_room(request, room_id):
    room = get_object_or_404(Room, name=room_id)
    player_name = request.session.get('player_name')

    if not player_name:
        return JsonResponse({'status': 'removed'})

    player_exists = room.players.filter(player_name=player_name).exists()

    if player_exists:
        return JsonResponse({'status': 'present'})

    return JsonResponse({'status': 'removed'})
