from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import random

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from main.abilities import change_inventory_randomly
from main.models import Room, Player, Gender, BodyBuild, HumanTrait, Speciality, Health, Hobby, Phobia, Inventory, \
    MoreInformation, SpecialFeature, Bunker, Cataclysm


def generate_random_name(length=10):
    all_char = 'qwertyuioplkjhgfdsazxcvbnm1234567890'
    return ''.join(random.choice(all_char) for _ in range(length))


def index(request):
    player_name = request.session.get('player_name')
    if player_name:
        player_rooms = Room.objects.filter(players__player_name=player_name)
    else:
        player_rooms = []

    return render(request, 'index.html', {'player_rooms': player_rooms})


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


def login(request, room_id):
    if request.method == 'POST':
        username = request.POST['username']
        room = Room.objects.get(name=room_id)
        if room.players.filter(player_name=username).exists():
            messages.info(request, "Username is already exists")
            return redirect('login', room_id=room_id)

        Player.objects.create(room=room, player_name=username)
        request.session['player_name'] = username
        return redirect('game_room', room_id=room.name)

    return render(request, 'login.html')


def game_room(request, room_id):
    player_name = request.session.get('player_name', None)
    if not player_name:
        return redirect('login', room_id=room_id)

    room = get_object_or_404(Room, name=room_id)
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


def categorize_age(number):
    if number < 18:
        value = "Teenagers"
    elif 18 <= number <= 35:
        value = "Young Adults"
    elif 35 < number <= 55:
        value = "Middle Age"
    elif 55 < number <= 75:
        value = "Senior Adults"
    else:
        value = "Elderly"
    return value


def create_random_player(player):
    if not player.gender:
        player.gender = Gender.objects.order_by('?').first()
    if not player.body_build:
        player.body_build = BodyBuild.objects.order_by('?').first()
    if not player.a_human_trait:
        player.a_human_trait = HumanTrait.objects.order_by('?').first()
    if not player.speciality:
        player.speciality = Speciality.objects.order_by('?').first()
    if not player.health:
        player.health = Health.objects.order_by('?').first()
    if not player.hobby:
        player.hobby = Hobby.objects.order_by('?').first()
    if not player.phobia:
        player.phobia = Phobia.objects.order_by('?').first()
    if not player.inventory:
        player.inventory = Inventory.objects.order_by('?').first()
    if not player.more_information:
        player.more_information = MoreInformation.objects.order_by('?').first()
    if not player.special_feature1:
        player.special_feature1 = SpecialFeature.objects.order_by('?').first()
    if not player.special_feature2:
        player.special_feature2 = SpecialFeature.objects.order_by('?').first()

    player.save()
    return player


def generate_side():
    bunker = random.choice(Bunker.objects.all())
    return bunker


def create_cataclysm():
    cataclysm_instance = random.choice(Cataclysm.objects.all())
    return cataclysm_instance


def start_game(request, room_id):
    room = get_object_or_404(Room, name=room_id)

    for player in room.players.all():
        create_random_player(player)

    if not room.bunker:
        room.bunker = generate_side()
        room.save()

    if not room.cataclysm:
        room.cataclysm = create_cataclysm()
        room.save()

    room.is_game_started = True
    room.save()

    player_name = request.session.get('player_name')
    player = get_object_or_404(Player, player_name=player_name, room=room)

    is_creator = room.creator.player_name == player_name
    request.session['number_of_players'] = room.players.count()

    return render(request, 'game_field.html', {
        'room': room,
        'player': player,
        'bunker': room.bunker,
        'cataclysm': room.cataclysm,
        'is_creator': is_creator,
        'number_of_players': room.players.count(),
    })


def check_game_started(request, room_id):
    room = get_object_or_404(Room, name=room_id)
    return JsonResponse({'is_game_started': room.is_game_started})


# def update_player_info(request):
#     if request.method == 'POST':
#         player_name = request.POST.get('player_name')
#         info_type = request.POST.get('info_type')
#         player = Player.objects.get(player_name=player_name)
#
#         if info_type == 'gender':
#             player.is_gender_open = True
#         elif info_type == 'body_build':
#             player.is_body_build_open = True
#         elif info_type == 'a_human_trait':
#             player.is_human_trait_open = True
#         elif info_type == 'speciality':
#             player.is_speciality_open = True
#         elif info_type == 'health':
#             player.is_health_open = True
#         elif info_type == 'hobby':
#             player.is_hobby_open = True
#         elif info_type == 'phobia':
#             player.is_phobia_open = True
#         elif info_type == 'inventory':
#             player.is_inventory_open = True
#         elif info_type == 'more_information':
#             player.is_more_information_open = True
#         elif info_type == 'special_feature1':
#             player.is_special_feature1_open = True
#         elif info_type == 'special_feature2':
#             player.is_special_feature2_open = True
#
#         player.save()
#         return JsonResponse({'status': 'success'})
#     return JsonResponse({'status': 'fail'})

def update_player_info(request):
    player_name = request.POST.get('player_name')
    info_type = request.POST.get('info_type')

    player = get_object_or_404(Player, player_name=player_name)
    setattr(player, f'is_{info_type}_open', True)
    player.save()

    return JsonResponse({'status': 'success'})


def vote_against_player(request):
    if request.method == 'POST':
        voted_player_id = request.POST.get('voted_player')
        voted_player = Player.objects.get(player_name=voted_player_id)

        return redirect('game_room', room_name=voted_player.room.name)
    return JsonResponse({'status': 'fail'})


@csrf_exempt
@require_POST
def activate_special_feature(request):
    player_id = request.POST.get('player_id')
    feature_type = request.POST.get('feature_type')
    action = request.POST.get('action')  # 'unlock' or 'lock'

    player = get_object_or_404(Player, id=player_id)
    feature = getattr(player, feature_type, None)

    if not feature:
        return JsonResponse({'status': 'error', 'message': 'Feature not found'})

    # Perform the action
    if action == 'unlock' and not getattr(player, f'is_{feature_type}_open', False):
        # Assuming the feature activation changes something
        # For example, changing an inventory or unlocking new abilities
        execute_feature(player, feature)
        setattr(player, f'is_{feature_type}_open', True)
        player.save()
        return JsonResponse({'status': 'success', 'message': 'Feature unlocked and activated'})
    elif action == 'lock':
        setattr(player, f'is_{feature_type}_open', False)
        player.save()
        return JsonResponse({'status': 'success', 'message': 'Feature locked'})

    return JsonResponse({'status': 'error', 'message': 'Invalid action or state'})