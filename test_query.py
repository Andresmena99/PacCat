import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')

django.setup()

from django.contrib.auth.models import User
from datamodel.models import Game, GameStatus, Move

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
    print("No hay partidas con un solo jugador, por lo que no se puede unir al jugador con id 11")
    exit(0)

# Sacamos la partida con el id mínimo
partida = Game.objects.get(id=id_min)

# metemos al usuario, y comenzamos la partida
partida.mouse_user = usuario2

# Al hacer save, se pone en status active
partida.save()

print("\n\nNos unimos a la partida con menor id, y realizamos los movimientos:\n")
Move.objects.create(
                game=partida, player=partida.cat_user, origin=2, target=11)

print(partida)
Move.objects.create(
                game=partida, player=partida.mouse_user, origin=59, target=52)
print(partida)
