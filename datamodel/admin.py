from django.contrib import admin

from datamodel.models import UserProfile


# Add in this class to customise the Admin Interface
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


# Update the registration to include this customised interface
admin.site.register(UserProfile)
