from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

# REVISAR estos imports son copypaste de lo anterior, igual sobra alguno
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse


#from datamodel import constants
from datamodel.forms import UserForm


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
    # REVISAR esta copiado de la anterior practica, faltan cosas

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('mouse_cat:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'mouse_cat/login.html', {'user_form': UserForm()})


@login_required
def logout_service(request):
    # REVISAR esta copiado de la anterior practica
    logout(request)
    return redirect(reverse('mouse_cat:index'))


def signup_service(request):
    # REVISAR
    return render(request, 'mouse_cat/signup.html')


def counter_service(request):
    # REVISAR
    return render(request, 'mouse_cat/counter.html')


def create_game_service(request):
    # REVISAR
    return render(request, 'mouse_cat/new_game.html')


def join_game_service(request):
    # REVISAR
    return render(request, 'mouse_cat/join_game.html')


def select_game_service(request):
    # REVISAR
    return render(request, 'mouse_cat/select_game.html')


def show_game_service(request):
    # REVISAR
    return render(request, 'mouse_cat/game.html')


