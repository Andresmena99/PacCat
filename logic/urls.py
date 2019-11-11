from django.urls import path
from logic import views
# from django.conf.urls import url

urlpatterns = [
    path('index/', views.index, name='index'),
    path('', views.index, name='landing'),
]