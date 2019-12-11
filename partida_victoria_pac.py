import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')

django.setup()

from datamodel.models import Game, Move

game = Game.objects.filter(id=14)
game = game[0]
user1 = game.cat_user
user2 = game.mouse_user

moves = [
    {"player": user1, "origin": 0, "target": 9},
    {"player": user2, "origin": 59, "target": 50},
    {"player": user1, "origin": 9, "target": 16},
    {"player": user2, "origin": 50, "target": 57},
    {"player": user1, "origin": 16, "target": 25},
    {"player": user2, "origin": 57, "target": 48},
    {"player": user1, "origin": 25, "target": 32},
    {"player": user2, "origin": 48, "target": 57},
    {"player": user1, "origin": 32, "target": 41},
    {"player": user2, "origin": 57, "target": 48},
    {"player": user1, "origin": 2, "target": 11},
    {"player": user2, "origin": 48, "target": 57},
    {"player": user1, "origin": 11, "target": 18},
    {"player": user2, "origin": 57, "target": 48},
    {"player": user1, "origin": 18, "target": 27},
    {"player": user2, "origin": 48, "target": 57},
    {"player": user1, "origin": 27, "target": 34},
    {"player": user2, "origin": 57, "target": 48},
    {"player": user1, "origin": 34, "target": 43},
    {"player": user2, "origin": 48, "target": 57},
    {"player": user1, "origin": 43, "target": 50},
    {"player": user2, "origin": 57, "target": 48},
    {"player": user1, "origin": 50, "target": 57},
    {"player": user2, "origin": 48, "target": 57},
]


for move in moves:
    Move.objects.create(game=game, player=move["player"],
                        origin=move["origin"], target=move["target"])