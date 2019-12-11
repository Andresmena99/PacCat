"""
    URLs correspondientes a toda la aplicación de PACGato.

    Author
    -------
        Andrés Mena
        Eric Morales
"""

from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    url(r'', include(('logic.urls', 'logic'), namespace='logic')),
    path('admin/', admin.site.urls),
    path('mouse_cat/', include('logic.urls'))
]
