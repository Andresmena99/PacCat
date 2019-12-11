"""
    Tests que comprueban la funcionalidad del sistema de victorias.

    Author
    -------
        Andrés Mena
"""
import re

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import Client, TransactionTestCase
from django.urls import reverse

from datamodel import constants
from datamodel.models import Game, GameStatus, Move


TEST_USERNAME_1 = "testUserMouseCatBaseTest_1"
TEST_PASSWORD_1 = "hskjdhfhw"
TEST_USERNAME_2 = "testUserMouseCatBaseTest_2"
TEST_PASSWORD_2 = "kj83jfbhg"


SHOW_GAME_SERVICE = "show_game"
PLAY_GAME_WAITING = "play_waiting"
SHOW_GAME_TITLE = r"<h1>Play</h1>|<h1>Jugar</h1>"

SERVICE_DEF = {
    SHOW_GAME_SERVICE: {
        "title": SHOW_GAME_TITLE,
        "pattern": r"(Board|Tablero): (?P<board>\[.*?\])"
    },
}


# Tests classes:
# - GameEndTests

class ServiceBaseTest(TransactionTestCase):
    def setUp(self):
        self.paramsUser1 = {"username": TEST_USERNAME_1, "password": TEST_PASSWORD_1}
        self.paramsUser2 = {"username": TEST_USERNAME_2, "password": TEST_PASSWORD_2}

        User.objects.filter(
            Q(username=self.paramsUser1["username"]) |
            Q(username=self.paramsUser2["username"])).delete()

        self.user1 = User.objects.create_user(
            username=self.paramsUser1["username"],
            password=self.paramsUser1["password"])
        self.user2 = User.objects.create_user(
            username=self.paramsUser2["username"],
            password=self.paramsUser2["password"])

        self.client1 = self.client
        self.client2 = Client()

    def tearDown(self):
        User.objects.filter(
            Q(username=self.paramsUser1["username"]) |
            Q(username=self.paramsUser2["username"])).delete()

    @classmethod
    def loginTestUser(cls, client, user):
        client.force_login(user)

    @classmethod
    def logoutTestUser(cls, client):
        client.logout()

    @classmethod
    def decode(cls, txt):
        return txt.decode("utf-8")





class GameRequiredBaseServiceTests(ServiceBaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        self.user1.games_as_cat.all().delete()
        self.user2.games_as_cat.all().delete()
        super().tearDown()


class PlayGameBaseServiceTests(GameRequiredBaseServiceTests):
    def setUp(self):
        super().setUp()

        self.sessions = [
            {"client": self.client1, "player": self.user1},
            {"client": self.client2, "player": self.user2},
        ]

    def tearDown(self):
        super().tearDown()

    def set_game_in_session(self, client, user, game_id):
        self.loginTestUser(client, user)
        session = client.session
        session[constants.GAME_SELECTED_SESSION_ID] = game_id
        session.save()


class GameEndTests(PlayGameBaseServiceTests):
    """Este test comprueba si ha ganado un gato o un PAC"""

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """Se realiza una secuencia de movimientos. En cada movimiento,
        se comprueba que el estado de la partida siga siendo activo, y que la
        respuesta de la página no sea la victoria ni de gato ni de PAC. En el
         último movimiento, hacemos que ganen los gatos porque encierran al
         PAC, y comprobamos que la partida pasa a estado finalizada, y que
         la pagina nos devuelve la respuesta de gato gana"""

        # Generamos una secuencia de movimientos que encierra al PAC
        # (excepto el ultimo movimiento)
        moves = [
            {"player": self.user1, "origin": 0, "target": 9},
            {"player": self.user2, "origin": 59, "target": 50},
            {"player": self.user1, "origin": 9, "target": 16},
            {"player": self.user2, "origin": 50, "target": 57},
            {"player": self.user1, "origin": 16, "target": 25},
            {"player": self.user2, "origin": 57, "target": 48},
            {"player": self.user1, "origin": 25, "target": 32},
            {"player": self.user2, "origin": 48, "target": 57},
            {"player": self.user1, "origin": 32, "target": 41},
            {"player": self.user2, "origin": 57, "target": 48},
            {"player": self.user1, "origin": 2, "target": 11},
            {"player": self.user2, "origin": 48, "target": 57},
            {"player": self.user1, "origin": 11, "target": 18},
            {"player": self.user2, "origin": 57, "target": 48},
            {"player": self.user1, "origin": 18, "target": 27},
            {"player": self.user2, "origin": 48, "target": 57},
            {"player": self.user1, "origin": 27, "target": 34},
            {"player": self.user2, "origin": 57, "target": 48},
            {"player": self.user1, "origin": 34, "target": 43},
            {"player": self.user2, "origin": 48, "target": 57},
            {"player": self.user1, "origin": 43, "target": 50},
            {"player": self.user2, "origin": 57, "target": 48},
            {"player": self.user1, "origin": 50, "target": 57},
        ]

        game = Game.objects.create(cat_user=self.user1, mouse_user=self.user2)
        game.save()
        self.set_game_in_session(self.client1, self.user1, game.id)

        # Todos estos movimientos tienen que dejar la partida como activa,
        # y no nos pueden llevar a la página de victoria ni de gato ni de PAC
        for move in moves:
            Move.objects.create(game=game, player=move["player"],
                                origin=move["origin"], target=move["target"])
            self.assertEqual(game.status, GameStatus.ACTIVE)
            response = self.client1.get(reverse(SHOW_GAME_SERVICE),
                                        follow=True)

            m = re.search(constants.CAT_WINNER, self.decode(response.content))
            self.assertFalse(m)
            m = re.search(constants.MOUSE_WINNER,
                          self.decode(response.content))
            self.assertFalse(m)

        # Este ultimo movimiento es el que se comen al PAC
        Move.objects.create(
            game=game, player=self.user2, origin=48, target=57)

        # Comprobamos que el juego pasa a estado finalizado
        self.assertEqual(game.status, GameStatus.FINISHED)

        # Comprobamos que nos ha llevado a la pagina de victoria del gato
        response = self.client1.get(reverse(SHOW_GAME_SERVICE), follow=True)
        m = re.search(constants.CAT_WINNER, self.decode(response.content))
        self.assertTrue(m)

        # Comprobamos que el juego ya no esta en la sesion, porque ha
        # finalizado
        self.assertFalse(self.client1.session.get(
            constants.GAME_SELECTED_SESSION_ID, False))

    def test2(self):
        """Igual que el test1, se realiza una secuencia de movimentos, pero
        en este caso el que gana es el gato, porque se coloca a la misma altura
        que el ultimo PAC, y eso lo marcamos como victoria del gato"""

        # Generamos una secuencia de movimientos que hace ganar al PAC
        # (excepto el ultimo movimiento)
        moves = [
            {"player": self.user1, "origin": 0, "target": 9},
            {"player": self.user2, "origin": 59, "target": 50},
            {"player": self.user1, "origin": 2, "target": 11},
            {"player": self.user2, "origin": 50, "target": 43},
            {"player": self.user1, "origin": 4, "target": 13},
            {"player": self.user2, "origin": 43, "target": 34},
            {"player": self.user1, "origin": 6, "target": 15},
            {"player": self.user2, "origin": 34, "target": 27},
            {"player": self.user1, "origin": 9, "target": 16},
            {"player": self.user2, "origin": 27, "target": 18},
            {"player": self.user1, "origin": 11, "target": 20},
            {"player": self.user2, "origin": 18, "target": 9},
            {"player": self.user1, "origin": 20, "target": 27},
        ]

        game = Game.objects.create(cat_user=self.user1, mouse_user=self.user2)
        game.save()
        self.set_game_in_session(self.client1, self.user1, game.id)

        # Todos estos movimientos tienen que dejar la partida como activa,
        # y no nos pueden llevar a la página de victoria ni de gato ni de PAC
        for move in moves:
            Move.objects.create(game=game, player=move["player"],
                                origin=move["origin"], target=move["target"])
            self.assertEqual(game.status, GameStatus.ACTIVE)
            response = self.client1.get(reverse(SHOW_GAME_SERVICE),
                                        follow=True)
            m = re.search(constants.CAT_WINNER, self.decode(response.content))
            self.assertFalse(m)
            m = re.search(constants.MOUSE_WINNER,
                          self.decode(response.content))
            self.assertFalse(m)

        # Este ultimo movimiento hace que el PAC (PAC) llegue al otro extremo
        # por lo que gana la partida
        Move.objects.create(
            game=game, player=self.user2, origin=9, target=2)

        self.assertEqual(game.status, GameStatus.FINISHED)

        # Comprobamos que nos ha llevado a la pagina de victoria del gato
        response = self.client1.get(reverse(SHOW_GAME_SERVICE), follow=True)
        m = re.search(constants.MOUSE_WINNER, self.decode(response.content))
        self.assertTrue(m)

        self.assertFalse(self.client1.session.get(
            constants.GAME_SELECTED_SESSION_ID, False))
