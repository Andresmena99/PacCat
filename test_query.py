import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')

django.setup()

from django.contrib.auth.models import User
from datamodel.models import Game, Move
from itertools import chain
try:
    usuario1 = User.objects.get(id=10)
except User.DoesNotExist:
    usuario1 = User.objects.create_user(id=10, username='user_with_id_10')

try:
    usuario2 = User.objects.get(id=11)
except User.DoesNotExist:
    usuario2 = User.objects.create_user(id=11, username='user_with_id_11')

# Creo una partida para el usuario con id 10
game = Game(cat_user=usuario1)
game.save()

# Saco todas las partidas que tienen un solo jugador (no tienen mouse_user)
un_solo_jugador = Game.objects.filter(mouse_user=None)

if len(un_solo_jugador) > 0:
    print("PARTIDAS CON UN SOLO JUGADOR (solo gato)")
    for partida in un_solo_jugador:
        print(partida)

    # Obtenemos el id_minimo de las partidas con un solo jugador
    id_min = un_solo_jugador.order_by('id')[0:1].get().id

else:
    print("No hay partidas con un solo jugador, por lo que no se puede unir "
          "al jugador con id 11")
    exit(0)

# Sacamos la partida con el id mínimo
partida1 = Game.objects.filter(id = 18)
partida2 = Game.objects.filter(id = 19)
print("------------------------")
print(partida1)
print("------------------------")
print(partida2)
print("------------------------")
result_list = list(chain(partida1, partida2))
print(result_list)
