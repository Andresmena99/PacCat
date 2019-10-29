from django.contrib.auth.models import User
from datamodel.models import Game, GameStatus, Move

# users = User.objects.all()
#
# flag = 0
# for usuario in users:
#     if usuario.id == 10:
#         print("\n\tYA EXISTE EL USUARIO CON ID 10\n")
#         flag = 1
#
# if flag == 0:
#     usuario10 = User.objects.get_or_create(id = 10)


# REVISAR: Que hacemos si ya existia un usuario con ese id?

if User.objects.get(id=10) is None:
    usuario1 = User.objects.create(id=10, name='user_with_id_10')
else:
    usuario1 = User.objects.get(id=10)

if User.objects.get(id=11) is None:
    usuario2 = User.objects.create(id=11, name='user_with_id_11')
else:
    usuario2 = User.objects.get(id=11)

# Creo una partida para el usuario con id 10
game = Game(cat_user=usuario1)


# Entre todas las partidas, miro las que solo tienen un jugador
un_solo_jugador = []
games = Game.objects.all()
for partida in games:
    if partida.mouse_user is None:
        un_solo_jugador.append(partida)

id_min = 0
if un_solo_jugador:
    print("PARTIDAS CON UN SOLO JUGADOR (solo gato)\n")
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

print("ESTA ES LA PARTIDA SOBRE LA QUE VAMOS A REALIZAR MODIFICACIONES:\n")
print(partida)

# metemos al usuario, y comenzamos la partida
partida.mouse_user = usuario2
partida.status = GameStatus.ACTIVE

moves = [
    {"player": partida.cat_user, "origin": 2, "target": 11},
    {"player": partida.mouse_user, "origin": 59, "target": 52},
]

Move.objects.create(
                game=partida, player=partida.cat_user, origin=2, target=11)

print(partida)
Move.objects.create(
                game=partida, player=partida.mouse_user, origin=59, target=52)

print(partida)
