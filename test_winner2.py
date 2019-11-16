import os

import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')

django.setup()

from django.contrib.auth.models import User
from datamodel.models import Game, Move
from logic.views import check_winner

try:
    player_cat = User.objects.get(id=100)
except User.DoesNotExist:
    player_cat = User.objects.create_user(id=100, username='user_with_id_100')

try:
    player_mouse = User.objects.get(id=101)
except User.DoesNotExist:
    player_mouse = User.objects.create_user(id=11, username='user_with_id_101')

# Creamos una partida con los dos jugadores
game = Game(cat_user=player_cat, mouse_user=player_mouse)
game.save()

# Generamos una secuencia de movimientos que encierra al raton
moves = [
    {"player": player_cat, "origin": 0, "target": 9},
    {"player": player_mouse, "origin": 59, "target": 50},
    {"player": player_cat, "origin": 2, "target": 11},
    {"player": player_mouse, "origin": 50, "target": 43},
    {"player": player_cat, "origin": 4, "target": 13},
    {"player": player_mouse, "origin": 43, "target": 34},
    {"player": player_cat, "origin": 6, "target": 15},
    {"player": player_mouse, "origin": 34, "target": 27},
    {"player": player_cat, "origin": 9, "target": 16},
    {"player": player_mouse, "origin": 27, "target": 18},
    {"player": player_cat, "origin": 11, "target": 20},
    {"player": player_mouse, "origin": 18, "target": 9}
]

print("---------------------")
print("Estado inicial de la partida")
print(game)
print("---------------------")

for move in moves:
    m = Move.objects.create(game=game, player=move['player'], origin=move['origin'], target=move['target'])
    if check_winner(game) != 0:
        if check_winner(game) == 1:
            print("Han ganado los gatos")
        elif check_winner(game) == 2:
            print("Ha ganado el raton")


print("---------------------")
print("Estado final de la partida")
print(game)
print("---------------------")
