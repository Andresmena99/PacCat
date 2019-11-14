from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

# from datamodel import constants
from datamodel.forms import UserForm
from datamodel.models import Counter, Game, GameStatus, Move
from logic.forms import SignupForm, MoveForm
from datamodel import constants


def incrementar_counter(request):
    if "counter" in request.session:
        request.session["counter"] += 1
    else:
        counter_session = 1
        request.session["counter"] = counter_session
    # Incrementamos el contador global
    Counter.objects.inc()


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception="Action restricted to anonymous users"))
        else:
            return f(request)

    return wrapped


def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict['msg_error'] = exception
    return render(request, "mouse_cat/error.html", context_dict)


def index(request):
    return render(request, 'mouse_cat/index.html')


@anonymous_required
def login_service(request):
    if request.method == 'POST':
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
                return HttpResponse("Your mouse_cat account is disabled.")
        else:
            # REVISAR: Aqui hay que devolver el formulario, pero con el mensaje de error.
            print("Invalid login details: {0}, {1}".format(username, password))
            # form = UserForm()
            # form.add_error('username', "ME CAGO EN LA LECHE")
            return render(request, 'mouse_cat/login.html',
                          {'user_form': UserForm()})
    else:
        return render(request, 'mouse_cat/login.html',
                      {'user_form': UserForm()})


@login_required
def logout_service(request):
    user = request.user
    logout(request)
    for key in request.session.keys():
        del request.session[key]

    return render(request, 'mouse_cat/logout.html', {'user': user})
    return redirect(reverse('logic:index'))


@anonymous_required
def signup_service(request):
    # POST
    if request.method == 'POST':
        formulario = SignupForm(request.POST)

        # Esto llamara a la funcion clean para hacer la comprobacion
        if formulario.is_valid():
            new_user = formulario.save()

            # Sacamos el valor de la contraseña, y se lo asignamos al usuario antes de guardar
            new_user.set_password(formulario.cleaned_data['password'])
            new_user.save()

            # Procedemos a iniciar sesion del usuario en la pagina
            new_user = authenticate(username=formulario.cleaned_data['username'],
                                    password=formulario.cleaned_data['password'])
            login(request, new_user)
        else:
            # Formulario invalido, devolvemos los errores
            return render(request,
                          'mouse_cat/signup.html', {'user_form': formulario})

    # Si el metodo es get, le damos un formulario para rellenarlo
    else:
        incrementar_counter(request)
        return render(request,
                      'mouse_cat/signup.html', {'user_form': SignupForm()})

    return render(request,
                  'mouse_cat/signup.html', {'user_form': None})


def counter_service(request):
    incrementar_counter(request)
    counter_global = Counter.objects.get_current_value()

    context_dict = {'counter_session': request.session["counter"],
                    'counter_global': counter_global}
    return render(request, 'mouse_cat/counter.html', context=context_dict)


@login_required
def create_game_service(request):
    # Creamos una partida asignandosela al usuario que esta dentro del sistema
    new_game = Game(cat_user=request.user)
    new_game.save()
    return render(request, 'mouse_cat/new_game.html', {'game': new_game})


@login_required
def join_game_service(request):
    # Tenemos que meter al usuario en la partida con id mas alto
    # Entre todas las partidas, miro las que solo tienen un jugador
    un_solo_jugador = []
    games = Game.objects.all()
    for partida in games:
        if partida.mouse_user is None:
            un_solo_jugador.append(partida)

    # Si no hay partidas con un solo jugador
    if len(un_solo_jugador) <= 0:
        return render(request, 'mouse_cat/join_game.html',
                      {'msg_error': "There is no available games|No hay juegos disponibles"})

    else:
        id_max = -999
        for partida in un_solo_jugador:
            # REVISAR: Un jugador no puede jugar contra si mismo? O si?
            if partida.id > id_max and partida.cat_user != request.user:
                id_max = partida.id

        if id_max == -999:
            # No puedo jugar contra mi mismo
            return render(request, 'mouse_cat/join_game.html',
                          {
                              'msg_error': "There is no available games|No hay juegos disponibles"})

        else:
            # Cojo la partida a la que quiero unir al jugador
            partida = Game.objects.get(id=id_max)

            request.session[constants.GAME_SELECTED_SESSION_ID] = id_max

            # Comienza la partida
            partida.mouse_user = request.user
            partida.save()

            return render(request, 'mouse_cat/join_game.html',
                          {'game': partida})


@login_required
def select_game_service(request, id=-1):
    if request.method == 'GET' and id == -1:
        # Muestro todos los juegos en los que estoy participando, ya sea como raton o gato
        # Tengo que añadir un campo id a cada partida, para luego poder hacer bien el template
        mis_juegos_cat = []
        mis_juegos_mouse = []

        games = Game.objects.all()
        for partida in games:
            if partida.status == GameStatus.ACTIVE:
                if partida.mouse_user == request.user:
                    mis_juegos_mouse.append(partida)

                elif partida.cat_user == request.user:
                    mis_juegos_cat.append(partida)

        context_dict = {}
        context_dict['as_cat'] = mis_juegos_cat
        context_dict['as_mouse'] = mis_juegos_mouse
        return render(request, 'mouse_cat/select_game.html', context_dict)

    # Parte de POST
    if id != -1:
        request.session[constants.GAME_SELECTED_SESSION_ID] = id

        return show_game_service(request)


@login_required
def show_game_service(request):
    try:
        game = Game.objects.filter(id=request.session[constants.GAME_SELECTED_SESSION_ID])[0]

        return createBoard(request, game)
    except KeyError:
        return render(request, "mouse_cat/error.html", {'msg_error': "No game selected"})


@login_required
def move_service(request):
    if request.method == 'POST':
        try:
            game = Game.objects.filter(id=request.session[constants.GAME_SELECTED_SESSION_ID])[0]
            form = MoveForm(request.POST)
            if form.is_valid():
                if game.cat_turn:
                    Move.objects.create(
                        game=game, player=game.cat_user,
                        origin=form.cleaned_data['origin'],
                        target=form.cleaned_data['target'])
                    game.save()

                else:
                    Move.objects.create(
                        game=game, player=game.mouse_user,
                        origin=form.cleaned_data['origin'],
                        target=form.cleaned_data['target'])
                    game.save()

            return createBoard(request, game)

        except KeyError:
            return HttpResponseNotFound("El juego seleccionado no existe")

    # GET: Tiene que dar error
    else:
        return HttpResponseNotFound("Invalid get on service move")


def createBoard(request, game):
    if game is not None:
        board = [0] * 64

        board[game.cat1] = 1
        board[game.cat2] = 1
        board[game.cat3] = 1
        board[game.cat4] = 1

        board[game.mouse] = -1

        return render(request, 'mouse_cat/game.html',
                      {'game': game, 'board': board,
                       'move_form': MoveForm()})
