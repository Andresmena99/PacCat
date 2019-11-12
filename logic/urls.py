from django.urls import path
from logic import views
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='landing'),
    path('index/', views.index, name='index'),
    path('login/', views.login_service, name='login'),
    path('logout/', views.logout_service, name='logout'),
    path('signup/', views.signup_service, name='signup'),
    path('counter/', views.counter_service, name='counter'),
    path('create_game/', views.create_game_service, name='create_game'),
    path('join_game/', views.join_game_service, name='join_game'),
    path('select_game/', views.select_game_service, name='select_game'),
    path('play/', views.show_game_service, name='show_game'),
    #path('move/', views.move_service, name='move'),
    # REVISAR este ultimo habra que añadirlo, pero aun no hace falta
]