from django.urls import path

from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('game/', views.game, name='game'),
    path('join_room/', views.join_room, name='join_room'),
    path('game_room/<str:room_id>/', views.game_room, name='game_room'),
    path('number_of_people/<str:room_id>/', views.number_of_people, name='number_of_people'),
    path('close_room/<str:room_id>', views.close_room, name='close_room'),
    path('exit_room/<str:room_id>', views.exit_room, name='exit_room'),
    path('remove_player/<str:room_id>/', views.remove_player, name='remove_player'),
    path('check_player_in_room/<str:room_id>/', views.check_player_in_room, name='check_player_in_room'),
]
