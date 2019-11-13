from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseForbidden
from django.shortcuts import render

# REVISAR estos imports son copypaste de lo anterior, igual sobra alguno
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

# from datamodel import constants
from datamodel.forms import UserForm
from datamodel.models import Counter, Game
from logic.forms import RegisterForm
from datamodel import constants


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request, exception="Action restricted to anonymous users"))
        else:
            return f(request)

    return wrapped


def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    return render(request, "mouse_cat/error.html", context_dict)


def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to the template engine.

    # Render the response and send it back!
    return render(request, 'mouse_cat/index.html')


# REVISAR a todos los siguientes les falta el codigo de dentro

@anonymous_required
def login_service(request):
    # REVISAR. No se porque no funciona...

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)

                return redirect(reverse('logic:index'))
            else:
                return HttpResponse("Your mouse_cat account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'mouse_cat/login.html', {'user_form': UserForm()})


@login_required
def logout_service(request):
    # REVISAR esta copiado de la anterior practica

    logout(request)
    return redirect(reverse('logic:index'))


# @anonymous_required
# def signup_service(request):
#     # Si el metodo es post, significa que se estan intentando registrar
#     if request.method == 'POST':
#
#         # Sacamos la informacion del formulario de registro
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             new_user = form.save()
#             new_user.set_password(form.cleaned_data.get('password1'))
#             new_user.save()
#
#         else:
#             # Imprimimos los errores del formulario por terminal
#             print(form.errors)
#
#     else:
#         # REVISAR: Habria que devolverlo sin el campo de alumnodb
#         return render(request, 'mouse_cat/signup.html', {'user_form': UserCreationForm()})
#
#     return render(request, 'mouse_cat/signup.html', {'user_form': None})

@anonymous_required
def signup_service(request):
    # POST
    if request.method == 'POST':
        formulario = RegisterForm(request.POST)

        #Esto llamara a la funcion clean para hacer la comprobacion
        if formulario.is_valid():
            new_user = formulario.save()

            #Sacamos el valor de la contraseña, y se lo asignamos al usuario antes de guardar
            new_user.set_password(formulario.cleaned_data['password'])
            new_user.save()
        else:
            # Formulario invalido, devolvemos los errores
            return render(request,
                          'mouse_cat/signup.html', {'user_form': formulario})

    # Si el metodo es get, le damos un formulario para rellenarlo
    else:
        return render(request,
                      'mouse_cat/signup.html', {'user_form': RegisterForm()})

    return render(request,
                  'mouse_cat/signup.html', {'user_form': None})


def counter_service(request):
    # REVISAR habra que poner Counter.objects.inc() en todos los sitios donde
    # hagamos una peticion para que esto funcione, tambien habra que actualizar
    # el contador que esta en la session.

    if "counter" in request.session:
        counter_session = request.session["counter"]
    else:
        counter_session = 0
        request.session["counter"] = counter_session

    counter_global = Counter.objects.get_current_value()

    context_dict = {'counter_session': counter_session, 'counter_global': counter_global}
    return render(request, 'mouse_cat/counter.html', context=context_dict)


@login_required
def create_game_service(request):
    new_game = Game(request.user)
    new_game.save()
    return render(request, 'mouse_cat/new_game.html', {'game': new_game})


def join_game_service(request):
    # REVISAR
    return render(request, 'mouse_cat/join_game.html')


def select_game_service(request):
    # REVISAR
    return render(request, 'mouse_cat/select_game.html')


def show_game_service(request):
    # REVISAR
    return render(request, 'mouse_cat/game.html')
