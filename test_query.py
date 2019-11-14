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

# Entre todas las partidas, miro las que solo tienen un jugador
un_solo_jugador = []
games = Game.objects.all()
for partida in games:
    if partida.mouse_user is None:
        un_solo_jugador.append(partida)

id_min = 0
if len(un_solo_jugador) > 0:
    print("PARTIDAS CON UN SOLO JUGADOR (solo gato)")
    for partida in un_solo_jugador:
        print(partida)

    # buscamos la partida con el id mínimo
    id_min = un_solo_jugador[0].id
    for partida in un_solo_jugador:
        if partida.id < id_min:
            id_min = partida.id

else:
    print("No hay partidas con un solo jugador, por lo que no se puede unir al jugado con id 11")
    exit(0)

# Sacamos la partida con el id mínimo
partida = Game.objects.get(id=id_min)

print("\n")
print("ESTA ES LA PARTIDA SOBRE LA QUE VAMOS A REALIZAR MODIFICACIONES:")
print(partida)
print("\n")

# metemos al usuario, y comenzamos la partida
partida.mouse_user = usuario2

#Al hacer save, se pone en status active
partida.save()

Move.objects.create(
                game=partida, player=partida.cat_user, origin=2, target=11).save()

print(partida)
Move.objects.create(
                game=partida, player=partida.mouse_user, origin=59, target=52).save()

print(partida)
