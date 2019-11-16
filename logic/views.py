from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from datamodel import constants
from datamodel.models import Counter, Game, GameStatus, Move, valid_move
from logic.forms import SignupForm, MoveForm, UserForm


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
        Funcion que genera la pagina html que muestra el resultado de una
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
    board = [0] * 64
    board[game.cat1] = 1
    board[game.cat2] = 1
    board[game.cat3] = 1
    board[game.cat4] = 1
    board[game.mouse] = -1

    # Cambiamos el estado de la partida a terminada
    game.status = GameStatus.FINISHED
    game.save()

    # Borramos de la sesion la partida, porque ya ha terminado
    if constants.GAME_SELECTED_SESSION_ID in request.session:
        del request.session[constants.GAME_SELECTED_SESSION_ID]

    # Devolvemos un página con un mensaje de ganador y el tablero final de la
    # partida
    context_dict = {}
    if winner == 1:
        context_dict['winner'] = constants.CAT_WINNER
    if winner == 2:
        context_dict['winner'] = constants.MOUSE_WINNER
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
            Andrés Mena
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
        formulario = SignupForm(request.POST)

        # Esto llamara a la funcion clean para hacer la comprobacion del
        # formulario
        if formulario.is_valid():
            new_user = formulario.save()

            # Sacamos el valor de la contraseña, y se lo asignamos al usuario
            # antes de guardar
            new_user.set_password(formulario.cleaned_data['password'])
            new_user.save()

            # Procedemos a iniciar sesion del usuario en la pagina
            new_user = authenticate(username=
                                    formulario.cleaned_data['username'],
                                    password=
                                    formulario.cleaned_data['password'])
            login(request, new_user)

            # Devolvemos una pagina que indica que se ha registrado
            # correctamente
            return render(request,
                          'mouse_cat/signup.html', {'user_form': None})

        else:
            # Formulario invalido, devolvemos los errores
            return render(request,
                          'mouse_cat/signup.html', {'user_form': formulario})

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
def select_game_service(request, id=-1):
    """
        Funcion que nos muestra todas las partidas existentes y nos permite
        comenzar a jugar en cualquiera de ellas con tan solo un click

        Parameters
        ----------
        request : HttpRequest
            Solicitud Http
        id : int (default -1)
            Id de la partida seleccionada para jugar, por defecto a -1
            lo cual quiere decir que queremos ver la lista de partidas.

        Returns
        -------
        Html : archivo html con una lista de partidas o con el tablero
               listo para jugar

        Author
        -------
            Eric Morales
    """

    if request.method == 'GET' and id == -1:
        # Tengo que añadir un campo id a cada partida, para luego poder hacer
        # bien el template

        # Filtro los juegos que estan activos, en los que el usuario que
        # hace la solicitud es el gato o el raton
        mis_juegos_cat = Game.objects.filter(status=GameStatus.ACTIVE,
                                             cat_user=request.user)
        mis_juegos_mouse = Game.objects.filter(status=GameStatus.ACTIVE,
                                               mouse_user=request.user)

        context_dict = {'as_cat': mis_juegos_cat, 'as_mouse': mis_juegos_mouse}
        return render(request, 'mouse_cat/select_game.html', context_dict)

    # En este caso, significa que quiero jugar la partida
    if id != -1:
        # Confirmo que no me esten dando un id que no es valido. En caso de
        # ser válido, intento devuelver el estado de la partida llamando a
        # show game service
        game = Game.objects.filter(id=id)
        if len(game) > 0:
            game = game[0]
            if game.status != GameStatus.ACTIVE:
                # Error porque el juego seleccionado no esta en estado activo
                return HttpResponseNotFound(
                    constants.ERROR_SELECTED_GAME_NOT_AVAILABLE)

            if game.cat_user != request.user and game.mouse_user != request.user:
                # Error porque el jugador que solicita el juego no es ni el
                # gato ni el raton
                return HttpResponseNotFound(
                    constants.ERROR_SELECTED_GAME_NOT_YOURS)

            request.session[constants.GAME_SELECTED_SESSION_ID] = id
            return show_game_service(request)

        # Error porque no se ha encontrado un juego con el id solicitado
        else:
            return HttpResponseNotFound(
                constants.ERROR_SELECTED_GAME_NOT_EXISTS)


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


@login_required
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
                except:
                    # Añadimos el error del movimiento al formulario
                    form.add_error(None, constants.MSG_ERROR_MOVE)

            # Hacemos una comprobacion de si la partida tiene que finalizar
            # por si ha ganado el raton o el gato
            check_end = check_winner(game)
            if check_end == 1 or check_end == 2:
                # Devolvemos la página con un mensaje de partida terminada
                # y con el tablero pintado
                return end_game(request, check_end, game)

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
        # Primero colocamos todas las casillas a 0, y luego donde estén los
        # gatos lo ponemos a 1, y donde esté el raton a -1
        board = [0] * 64

        board[game.cat1] = 1
        board[game.cat2] = 1
        board[game.cat3] = 1
        board[game.cat4] = 1

        board[game.mouse] = -1

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


def check_winner(game):
    """
        Funcion que comprueba si hay ganador.

        Parameters
        ----------
        game : Game
            Partida correspondiente

        Returns
        -------
        int : función que indica cual ha sido el ganador de una partida,
              los posibles resultados son los siguientes:
                - 0 == NO WINNER
                - 1 == CAT_WINNER
                - 2 == MOUSE_WINNER

        Author
        -------
            Andrés Mena
    """

    if game is not None:
        # Sacamos la posicion de cada gato y raton, con sus coordenadas x e y
        cat1 = game.cat1
        cat1x = cat1 // 8 + 1

        cat2 = game.cat2
        cat2x = cat2 // 8 + 1

        cat3 = game.cat3
        cat3x = cat3 // 8 + 1

        cat4 = game.cat4
        cat4x = cat4 // 8 + 1

        mouse = game.mouse
        mousex = mouse // 8 + 1

        # Primero comprobamos la condicion de victoria del mouse
        # En cuanto el mouse se encuentre a la misma altura que el último
        # gato, significa que ya ha ganado (si hace movimientos logicos
        # claro
        if (mousex <= cat1x and mousex <= cat2x and mousex <= cat3x and
                mousex <= cat4x):
            # EL RATON HA GANADO PORQUE SE ENCUENTRA A LA MISMA ALTURA
            return 2
            # Revisar: Finalizar la partida

        if not game.cat_turn:
            # El otro caso, es que el raton se vea rodeado
            # Probamos el movimiento a todas las posibles casillas del gato
            flag = 0
            for i in range(Game.MIN_CELL, Game.MAX_CELL):
                try:
                    if valid_move(game, mouse, i):
                        # Si tengo un movimiento valido, todavia no he perdido
                        flag = 1
                except:
                    pass

            if flag == 0:
                # El raton pierde porque no puede hacer ningun movimiento
                return 1

        # Si llegamos aqui, es porque no hay ganador
        return 0
