"""
    Vistas utilizadas a lo largo de la aplicación de RatonGato.

    Author
    -------
        Andrés Mena
        Eric Morales
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from datamodel import constants
from datamodel.models import Counter, Game, GameStatus, Move, check_winner
from logic.forms import SignupForm, MoveForm, UserForm
from itertools import chain


def anonymous_required(f):
    """
        Decorador para limitar funciones a usuarios anonimos.

        Parameters
        ----------
        f : funcion
            Funcion a ejecutar

        Returns
        -------
        HttpResponse : error o la respuesta de la funcion.

        Author
        -------
            Profesores PSI
    """

    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception=constants.ERROR_RESTRICTED_ANONYMOUS))
        else:
            return f(request)

    return wrapped


def errorHTTP(request, exception=None):
    """
        Crea un error http basadp en una solicitud y lo devuelve

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http
        exception : string
            Almacena el error a mostrar.

        Returns
        -------
        HttpResponse : error o la respuesta de la funcion.

        Author
        -------
            Profesores PSI
    """
    context_dict = {'msg_error': exception}
    return render(request, "mouse_cat/error.html", context_dict)


def end_game(request, winner, game):
    """
        Funcion que genera la pagina html que muestra el resultado final de una
        partida.

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http
        winner : int
            Indica quien ha sido el ganador de la partida:
                - winner == 1: ganador gato
                - winner == 2: ganador ratón
        game : Game
            Juego actual

        Returns
        -------
        Html : archivo html con el resumen de final de partida.

        Author
        -------
            Andrés Mena
    """

    # La partida ha terminado. Imprimiremos una ultima vez el
    # tablero
    board = create_board_from_game(game)

    # Borramos de la sesion la partida, porque ya ha terminado
    if constants.GAME_SELECTED_SESSION_ID in request.session:
        del request.session[constants.GAME_SELECTED_SESSION_ID]

    # Devolvemos un página con un mensaje de ganador y el tablero final de la
    # partida
    context_dict = {}

    # Felicitamos al usuario que ha ganado
    if winner == 1:
        if request.user == game.cat_user:
            msg = constants.CAT_WINNER + ". Enhorabuena " + str(request.user)
            context_dict['winner'] = msg
        else:
            msg = constants.CAT_WINNER + ". Sigue practicando " + str(request.user)
            context_dict['winner'] = msg
    if winner == 2:
        if request.user == game.mouse_user:
            msg = constants.MOUSE_WINNER + ". Enhorabuena " + str(request.user)
            context_dict['winner'] = msg
        else:
            msg = constants.MOUSE_WINNER + ". Sigue practicando " + str(request.user)
            context_dict['winner'] = msg

    context_dict['board'] = board
    return render(request, "mouse_cat/end_game.html", context_dict)


def index(request):
    """
        Funcion que genera la pagina html inicial.

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http

        Returns
        -------
        Html : archivo html con la página incial

        Author
        -------
            Eric Morales
    """
    return render(request, 'mouse_cat/index.html')


@anonymous_required
def login_service(request):
    """
        Funcion que genera la pagina html con los formularios para inciar
        sesión (método GET) y de recibir estos formularios (método POST).

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http

        Returns
        -------
        Html : archivo html con el formulario de login.

        Author
        -------
            Andrés Mena
    """

    # Si alguien esta intentando iniciar sesion, es metodo post
    if request.method == 'POST':
        form = UserForm(request.POST)

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)

                # Reseteo el contador
                request.session["counter"] = 0

                return redirect(reverse('logic:index'))
            else:
                return HttpResponse(constants.EEROR_ACCOUNT_DISABLED)
        else:
            # Borramos los errores del formulario en caso de que los hubiera
            form.errors.pop('username', None)

            # Añadimos el error de autentificacion invalida
            form.add_error('username', constants.ERROR_CREDENTIALS)
            return render(request, 'mouse_cat/login.html',
                          {'user_form': form})

    # Metodo get implica que alguien está intentando ver la pagina
    else:
        return render(request, 'mouse_cat/login.html',
                      {'user_form': UserForm()})


@login_required
def logout_service(request):
    """
        Funcion que se encarga de cerrar la sesión de los usuarios y
        genera la pagina html informando de que el cierre se ha realizado
        correctamente.

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http

        Returns
        -------
        Html : archivo html con el resultado del logout.

        Author
        -------
            Eric Morales
    """

    # Obtenemos que usuario estas conectado, y procedemos a cerrar sesion
    user = request.user
    logout(request)

    # Eliminamos la informacion de la sesion
    for key in request.session.keys():
        del request.session[key]

    return render(request, 'mouse_cat/logout.html', {'user': user})


@anonymous_required
def signup_service(request):
    """
        Funcion que genera la pagina html con los formularios para registrarse
        (método GET) y de recibir estos formularios (método POST).

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http

        Returns
        -------
        Html : archivo html con el formulario de registro.

        Author
        -------
            Andrés Mena
    """

    # Si el metodo es post, significa que nos estan mandando un formulario con
    # informacion de inicio de sesion
    if request.method == 'POST':
        form = SignupForm(request.POST)

        # Esto llamara a la funcion clean para hacer la comprobacion del
        # formulario
        if form.is_valid():
            new_user = form.save()

            # Sacamos el valor de la contraseña, y se lo asignamos al usuario
            # antes de guardar
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()

            # Procedemos a iniciar sesion del usuario en la pagina
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password'])
            login(request, new_user)

            # Devolvemos una pagina que indica que se ha registrado
            # correctamente
            return render(request,
                          'mouse_cat/signup.html', {'user_form': None})

        else:
            # Formulario invalido, devolvemos los errores
            return render(request,
                          'mouse_cat/signup.html', {'user_form': form})

    # Si el metodo es get, es la primera vez que accede a la página, por lo
    # que le damos un formulario nuevo para que lo rellene
    else:
        return render(request,
                      'mouse_cat/signup.html', {'user_form': SignupForm()})


def counter_service(request):
    """
        Funcion que genera la pagina html para mostrar el valor del counter
        y que se encarga de incrementarlo en cada solicitud.

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http

        Returns
        -------
        Html : archivo html con el estado del counter.

        Author
        -------
            Eric Morales
    """

    # Si el contador ya esta definido en la sesion, lo incrementamos en 1
    if "counter" in request.session:
        request.session["counter"] += 1

    # En caso de no tener todavia contador en la sesion, lo inicializamos a 1
    else:
        counter_session = 1
        request.session["counter"] = counter_session

    # Incrementamos el contador global
    Counter.objects.inc()

    context_dict = {'counter_session': request.session["counter"],
                    'counter_global': Counter.objects.get_current_value()}
    return render(request, 'mouse_cat/counter.html', context=context_dict)


@login_required
def create_game_service(request):
    """
        Funcion que crea una partida nueva y muestra una pagina avisando
        de ello.

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http

        Returns
        -------
        Html : archivo html con el resultado de la creación de la partida.

        Author
        -------
            Andrés Mena
    """

    # Creamos una partida asignandosela al usuario que esta dentro del sistema
    new_game = Game(cat_user=request.user)
    new_game.save()
    return render(request, 'mouse_cat/new_game.html', {'game': new_game})


@login_required
def join_game_service(request):
    """
        Funcion que nos 'mete' en una partida existente y muestra una
        pagina avisando de ello.

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http

        Returns
        -------
        Html : archivo html con el resultado de unirnos a una partida.

        Author
        -------
            Andrés Mena
    """

    # Tenemos que meter al usuario en la partida con id mas alto
    # Entre todas las partidas, miro las que solo tienen un jugador
    un_solo_jugador = Game.objects.filter(mouse_user=None)

    # Si no hay partidas con un solo jugador
    if len(un_solo_jugador) <= 0:
        return render(request, 'mouse_cat/join_game.html',
                      {'msg_error': constants.MSG_ERROR_NO_AVAILABLE_GAMES})

    # Ordeno las partidas por id de forma descendente para hacer una busqueda
    # mas eficaz
    else:
        for partida in un_solo_jugador.order_by('-id'):
            # Me unire a la partida si yo no soy el propio gato, es decir,
            # no voy a jugar contra mi mismo
            if partida.cat_user != request.user:
                request.session[constants.GAME_SELECTED_SESSION_ID] = \
                    partida.id
                partida.mouse_user = request.user
                partida.save()
                return render(request, 'mouse_cat/join_game.html',
                              {'game': partida})

        return render(request, 'mouse_cat/join_game.html',
                      {
                          'msg_error': constants.MSG_ERROR_NO_AVAILABLE_GAMES})


@login_required
def select_game_service(request, tipo=-1, game_id=-1):
    """
        Funcion que nos muestra todas las partidas existentes y nos permite
        comenzar a jugar en cualquiera de ellas con tan solo un click

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http
        type : int (default -1)
            Tipo de servicio que queremos usar:
                1: Mostrar partidas que estamos jugando
                2: Mostrar partidas a las que nos podemos unir
                3: Mostrar partidas para reproducir

        game_id : int (default -1)
            Id de la partida seleccionada para jugar, por defecto a -1

        Returns
        -------
        Html : archivo html con una lista de partidas o con el tablero
               listo para jugar

        Author
        -------
            Eric Morales
    """
    # Esto significa que quiero ver las partidas que estoy jugando
    if request.method == 'GET' and int(tipo) == 1 and int(game_id) == -1:
        # Tengo que añadir un campo id a cada partida, para luego poder hacer
        # bien el template

        # Filtro los juegos que estan activos, en los que el usuario que
        # hace la solicitud es el gato o el raton
        mis_juegos_cat = Game.objects.filter(status=GameStatus.ACTIVE,
                                             cat_user=request.user)
        mis_juegos_mouse = Game.objects.filter(status=GameStatus.ACTIVE,
                                               mouse_user=request.user)

        context_dict = {'games_as_cat': mis_juegos_cat, 'games_as_mouse': mis_juegos_mouse}
        return render(request, 'mouse_cat/select_game.html', context_dict)

    # En este caso, significa que quiero jugar la partida
    elif request.method == 'GET' and int(tipo) == 1 and int(game_id) != -1:
        # Confirmo que no me esten dando un id que no es valido. En caso de
        # ser válido, intento devuelver el estado de la partida llamando a
        # show game service
        game = Game.objects.filter(id=game_id)
        if len(game) > 0:
            game = game[0]
            if game.status == GameStatus.CREATED:
                # Error porque el juego seleccionado no esta en estado activo
                return HttpResponseNotFound(
                    constants.ERROR_SELECTED_GAME_NOT_AVAILABLE)

            # Si la partida a terminado, nos muestra el ultimo estado de la partida
            if game.status == GameStatus.FINISHED and (
                    game.cat_user == request.user or game.mouse_user == request.user):
                return end_game(request, check_winner(game), game)

            if game.cat_user != request.user \
                    and game.mouse_user != request.user:
                # Error porque el jugador que solicita el juego no es ni el
                # gato ni el raton
                return HttpResponseNotFound(
                    constants.ERROR_SELECTED_GAME_NOT_YOURS)

            request.session[constants.GAME_SELECTED_SESSION_ID] = game_id
            return show_game_service(request)

        # Error porque no se ha encontrado un juego con el id solicitado
        else:
            return HttpResponseNotFound(
                constants.ERROR_SELECTED_GAME_NOT_EXISTS)

    # Quiero ver las partidas a las que me quiero unir
    elif request.method == 'GET' and int(tipo) == 2 and int(game_id) == -1:
        # Entre todas las partidas, miro las que solo tienen un jugador
        one_player = Game.objects.filter(mouse_user=None, status=GameStatus.CREATED)

        # Tengo que dejar en las que el jugador no sea el propio mouse_user,
        # ya que un jugador no puede jugar contra si mismo
        un_solo_jugador = []
        for partida in one_player.order_by('id'):
            if partida.cat_user != request.user:
                un_solo_jugador.append(partida)

        # Imprimo todas las partidas disponibles para el usuario
        return render(request, 'mouse_cat/join_game.html',
                      {'un_solo_jugador': un_solo_jugador})

    # Este caso significa que el usuario ya me ha dicho a que partida se quiere unir
    elif request.method == 'GET' and int(tipo) == 2 and int(game_id) != -1:
        # Compruebo que la partida siga estando disponible (la puede haber
        # cogido otro jugador mientras yo esperaba a seleccionarla)
        game = Game.objects.filter(id=game_id)
        if len(game) > 0:
            game = game[0]
            print(game)
            print(game.status != GameStatus.ACTIVE)
            print(game.mouse_user is None)
            if game.status != GameStatus.CREATED or game.mouse_user is not None:
                return render(request, 'mouse_cat/join_game.html',
                              {'msg_error': constants.ERROR_SELECTED_GAME_NOT_AVAILABLE})

            # Le meto en la partida y empieza el juego
            else:
                request.session[constants.GAME_SELECTED_SESSION_ID] = game_id
                game.mouse_user = request.user
                game.save()
                return show_game_service(request)


        else:
            return render(request, 'mouse_cat/join_game.html',
                          {'msg_error': constants.ERROR_SELECTED_GAME_NOT_EXISTS})

    # Muestro todas las partidas finalizadas en las que yo era alguno de los
    # participantes
    elif request.method == 'GET' and int(tipo) == 3 and int(game_id) == -1:
        finished_as_cat = Game.objects.filter(status=GameStatus.FINISHED, cat_user=request.user).order_by('id')
        finished_as_mouse = Game.objects.filter(status=GameStatus.FINISHED, mouse_user=request.user).order_by('id')
        context_dict = {'finished_as_cat': finished_as_cat, 'finished_as_mouse': finished_as_mouse}

        return render(request, "mouse_cat/finished_games.html", context_dict)

    # Entrar en modo reproduccion
    elif request.method == 'GET' and int(tipo) == 3 and int(game_id) != -1:
        # Almacenamos en la sesion el juego que se está reproduciendo
        request.session[constants.GAME_SELECTED_REPRODUCE_SESSION_ID] = game_id
        return reproduce_game_service(request)


@login_required
def show_game_service(request):
    """
        Funcion que nos muestra el juego seleccionado listo para jugar.

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http

        Returns
        -------
        Html : archivo html con con el tablero listo para jugar.

        Author
        -------
            Andrés Mena
    """

    # Muestra el estado de la partida que se encuentra en la sesion. En caso
    # de que no se haya ninguna partida en la sesion, devuelve un mensaje de
    # error
    try:
        game = Game.objects.filter(id=request.session[
            constants.GAME_SELECTED_SESSION_ID])[0]

        # Compruebo si la partida ha terminado ya, porque el otro jugador haya
        # ganado, en cuyo caso afirmativo tendré que llamar a la función de
        # partida finalizada
        if game.status == GameStatus.FINISHED:
            return end_game(request, check_winner(game), game)

        return create_board(request, game)
    except KeyError:
        return render(request, "mouse_cat/error.html",
                      {'msg_error': "No game selected"})


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def move_service(request):
    """
        Funcion que realiza el movimiento solicitado por el formulario
        MoveForm usando el método POST y muestra el resultado del mismo.

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http

        Returns
        -------
        Html : archivo html con el resultado del movimiento, ya sea el
        tablero actualizado, el final del juego o un error.

        Author
        -------
            Andrés Mena
    """

    if request.method == 'POST':
        # Nos mandan un formulario que contiene el movimento que se quiere
        # realizar.
        try:
            # Sacamos la partida que se esta jugando de la sesión
            game = Game.objects.filter(id=request.session[
                constants.GAME_SELECTED_SESSION_ID])[0]
            form = MoveForm(request.POST)
            if form.is_valid():
                # Intentamos hacer el movimiento. En caso de que nos de una
                # excepcion, significa que el moviemiento no estaba permitido
                try:
                    if game.cat_turn:
                        Move.objects.create(
                            game=game, player=game.cat_user,
                            origin=form.cleaned_data['origin'],
                            target=form.cleaned_data['target'])

                    else:
                        Move.objects.create(
                            game=game, player=game.mouse_user,
                            origin=form.cleaned_data['origin'],
                            target=form.cleaned_data['target'])
                except ValidationError:
                    # Añadimos el error del movimiento al formulario
                    form.add_error(None, constants.MSG_ERROR_MOVE)

            # Hacemos una comprobacion de si la partida tiene que finalizar
            # por si ha ganado el raton o el gato

            # REVISAR:
            # check_end = check_winner(game)
            # if check_end == 1 or check_end == 2:
            # Devolvemos la página con un mensaje de partida terminada
            # y con el tablero pintado
            # Si la partida ha terminado, significa que tenemos que mostrar
            # el tablero una ultima vez y devolver la pagina con el mensaje
            # de partida terminada
            if game.status == GameStatus.FINISHED:
                return end_game(request, check_winner(game), game)

            # Generamos de nuevo el tablero, pero se manda un formulario que
            # puede contener el error en el movimiento
            return create_board(request, game, form)

        # Si intentamos sacar un id de un juego que no existe, nos dará
        # este error
        except KeyError:
            return HttpResponseNotFound(
                constants.ERROR_SELECTED_GAME_NOT_EXISTS)

    # GET: Tiene que dar error. No se puede llamar a este servicio en modo get
    else:
        return HttpResponseNotFound(constants.ERROR_INVALID_GET)


@login_required
def finished_games(request):
    """
        REVISAR: COMENTAR
    """

    # Tenemos que meter al usuario en la partida con id mas alto
    # Entre todas las partidas, miro las que solo tienen un jugador
    finalizadas_raton = Game.objects.filter(status=GameStatus.FINISHED, mouse_user=request.user).order_by('id')
    finalizadas_gato = Game.objects.filter(status=GameStatus.FINISHED, cat_user=request.user).order_by('id')

    partidas_finalizadas = list(chain(finalizadas_raton, finalizadas_gato))
    if len(partidas_finalizadas) > 0:
        return render(request, 'mouse_cat/finished_games.html', {'finished': partidas_finalizadas})

    return render(request, 'mouse_cat/finished_games.html')


@login_required
def reproduce_game_service(request):
    """PARAMETROS DE ENTRADA:
        Nos mandan un formulario:
            1: Next
            -1: Previous
            2: Play
    """
    game_id = request.session[constants.GAME_SELECTED_REPRODUCE_SESSION_ID]
    game = Game.objects.filter(id=game_id)

    # No hay ninguna partida con el id
    if len(game) == 0:
        return errorHTTP(request,
                         constants.ERROR_SELECTED_GAME_NOT_EXISTS)

    game = game[0]

    # La partida no ha finalizado todavia
    if game.status != GameStatus.FINISHED:
        return errorHTTP(request,
                         constants.ERROR_NOT_FINISHED_YET)

    # Si no somos ni el raton ni el gato, no podemos visualizar la partida
    if not (game.cat_user == request.user or game.mouse_user == request.user):
        return errorHTTP(request,
                         constants.ERROR_NOT_ALLOWED_TO_REPRODUCE)

    # Esto es cuando nos mandan un formulario de movimiento
    if request.method == "POST":
        # Esto esta "mal", el enunciado no quiere que lo programemos asi...
        print("----------------")
        move = int(request.POST.get("Movimiento"))
        json_dict = get_move_service(request, move)

        # Una vez tenemos el diccionario de json, ya podemos imprimir el tablero con el movimiento hecho.
        # El tablero lo habiamos almacenado en la sesion
        board = request.session[constants.GAME_REPRODUCE_BOARD]
        cat_origin = board[json_dict['origin']]
        board[json_dict['origin']] = 0
        board[json_dict['target']] = cat_origin
        request.session[constants.GAME_REPRODUCE_BOARD] = board

        context_dict = {'game': game, 'board': board}

        # Si no hay mas movimientos, significa que ha terminado. Felicitamos al ganador
        if json_dict['next'] == 0:
            winner = check_winner(game)

            # Felicitamos al usuario que ha ganado
            if winner == 1:
                if request.user == game.cat_user:
                    msg = "Cats. Enhorabuena " + str(request.user)
                    context_dict['winner'] = msg
                else:
                    msg = "Cats. Sigue practicando " + str(request.user)
                    context_dict['winner'] = msg
            if winner == 2:
                if request.user == game.mouse_user:
                    msg = "Mouse. Enhorabuena " + str(request.user)
                    context_dict['winner'] = msg
                else:
                    msg = "Mouse. Sigue practicando " + str(request.user)
                    context_dict['winner'] = msg

        return render(request, 'mouse_cat/reproduce_game.html', context_dict)

    # Coloco el tablero en la posicion inicial
    if request.method == "GET":
        # Ponemos a 0 el movimiento por le que vamos reproduciendo
        request.session[constants.GAME_SELECTED_MOVE_NUMBER] = 0

        # Creo un tablero con los gatos en las posiciones iniciales
        board = [0] * 64
        board[0] = 1
        board[2] = 2
        board[4] = 3
        board[6] = 4
        board[59] = -1
        request.session[constants.GAME_REPRODUCE_BOARD] = board

        context_dict = {'game': game, 'board': board}

        return render(request, 'mouse_cat/reproduce_game.html', context_dict)


def create_board(request, game, form=None):
    """
        Funcion que devuelve el tablero de la partida pasada como parámetro,
        devolviendo además los errores correspondientes, si los hay

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http
        game : Game
            Partida correspondiente
        form : Form (default None)
            Formulario que contiene los errores correspondientes al ultimo
            movimiento que se ha intentado realizar

        Returns
        -------
        Html : archivo html con el resultado del movimiento, ya sea el
        tablero actualizado, el final del juego o un error.

        Author
        -------
            Eric Morales
    """

    # Creamos el array que representa el tablero
    if game is not None:
        # Creamos el tablero
        board = create_board_from_game(game)

        # Si nos han mandado un formulario, significa que puede tener errores,
        # asi que devolvemos el tablero con el formulario correspondiente
        if form is not None:
            return render(request, 'mouse_cat/game.html',
                          {'game': game, 'board': board,
                           'move_form': form})

        # Si no nos han dado formulario, significa que no se ha intentado hacer
        # todavia una solicitud de movimiento, por lo que creamos nosotros el
        # formulario vacio
        return render(request, 'mouse_cat/game.html',
                      {'game': game, 'board': board,
                       'move_form': MoveForm()})


# Funcion que simplemente devuelve el tablero en funcion del estado de la partida
def create_board_from_game(game):
    # Primero colocamos todas las casillas a 0, y luego donde estén los
    # gatos lo ponemos a 1, y donde esté el raton a -1
    board = [0] * 64
    board[game.cat1] = 1
    board[game.cat2] = 2
    board[game.cat3] = 3
    board[game.cat4] = 4
    board[game.mouse] = -1

    return board


# Esta funcion nos devuelve el json que nos pide el enunciado,
def get_move_service(request, shift):
    game = Game.objects.filter(id=request.session[constants.GAME_SELECTED_REPRODUCE_SESSION_ID])
    if len(game) == 0:
        return HttpResponse("ERROR")

    game = game[0]

    moves = Move.objects.filter(game=game).order_by('id')
    move_number = request.session[constants.GAME_SELECTED_MOVE_NUMBER]
    if shift == -1:
        move_number -= 1

    # En move number tenemos el indice movimiento que queremos realizar de moves
    if move_number < 0 or move_number >= len(moves):
        print("ERROR EL MOVIMIENTO ESTA FUERA DE INDICE")
        return HttpResponse("ERROR mirar terminal")

    real_move = moves[move_number]

    # En el diccionario, los campos previous y next se identifican con 1 (true)
    # y 0 (false)
    json_dict = {}
    if shift == 1:
        json_dict['origin'] = real_move.origin
        json_dict['target'] = real_move.target
    else:
        json_dict['origin'] = real_move.target
        json_dict['target'] = real_move.origin

    json_dict['previous'] = 1 if move_number > 0 else 0
    json_dict['next'] = 1 if move_number < len(moves) - 1 else 0

    if shift == 1:
        request.session[constants.GAME_SELECTED_MOVE_NUMBER] += 1
    elif shift == -1:
        request.session[constants.GAME_SELECTED_MOVE_NUMBER] -= 1

    print(json_dict)
    return json_dict
