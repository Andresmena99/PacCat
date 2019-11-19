import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')

django.setup()

from django.contrib.auth.models import User
from datamodel.models import Game, Move

cat_user = User.objects.filter(username='Ericgh9')
cat_user = cat_user[0]
mouse_user = User.objects.filter(username='Andresmena')
mouse_user = mouse_user[0]

game = Game.objects.filter(id=43)
game = game[0]
moves = [
    {"player": cat_user, "origin": 0, "target": 9},
    {"player": mouse_user, "origin": 59, "target": 50},
    {"player": cat_user, "origin": 9, "target": 16},
    {"player": mouse_user, "origin": 50, "target": 57},
    {"player": cat_user, "origin": 16, "target": 25},
    {"player": mouse_user, "origin": 57, "target": 48},
    {"player": cat_user, "origin": 25, "target": 32},
    {"player": mouse_user, "origin": 48, "target": 57},
    {"player": cat_user, "origin": 32, "target": 41},
    {"player": mouse_user, "origin": 57, "target": 48},
    {"player": cat_user, "origin": 2, "target": 11},
    {"player": mouse_user, "origin": 48, "target": 57},
    {"player": cat_user, "origin": 11, "target": 18},
    {"player": mouse_user, "origin": 57, "target": 48},
    {"player": cat_user, "origin": 18, "target": 27},
    {"player": mouse_user, "origin": 48, "target": 57},
    {"player": cat_user, "origin": 27, "target": 34},
    {"player": mouse_user, "origin": 57, "target": 48},
    {"player": cat_user, "origin": 34, "target": 43},
    {"player": mouse_user, "origin": 48, "target": 57},
    {"player": cat_user, "origin": 43, "target": 50},
    {"player": mouse_user, "origin": 57, "target": 48},
    {"player": cat_user, "origin": 50, "target": 57},

]

for move in moves:
    Move.objects.create(game=game, player=move["player"],
                        origin=move["origin"], target=move["target"])
