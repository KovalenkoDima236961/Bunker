from django.urls import path

from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('game/', views.game, name='game'),
    path('join_room/', views.join_room, name='join_room'),
    path('game_room/<int:room_id>/', views.game_room, name='game_room'),
]