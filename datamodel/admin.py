from django.contrib import admin

from datamodel.models import Game, Move
from datamodel.models import UserProfile


# REVISAR creo que hay que borrar esto
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


# Update the registration to include this customised interface
admin.site.register(UserProfile)
admin.site.register(Game)
admin.site.register(Move)
