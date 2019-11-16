"""
    Administración de toda la aplicación de RatonGato.

    Author
    -------
        Andrés Mena
        Eric Morales
"""

from django.contrib import admin

from datamodel.models import Game, Move
from datamodel.models import UserProfile


# REVISAR creo que hay que borrar esto
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class PageAdmin(admin.ModelAdmin):
    """
        Pagina para el administrador

        Attributes
        ----------
        list_display : array

        Methods
        -------
        none
    """
    list_display = ('title', 'category', 'url')


admin.site.register(UserProfile)
admin.site.register(Game)
admin.site.register(Move)
