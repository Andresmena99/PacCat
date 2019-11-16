import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')

django.setup()
from datamodel.models import Category, Page


def populate():
    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.

    # Lista de diccionarios

    python_pages = [
        {'title': 'Official Python Tutorial',
         'url': 'http://docs.python.org/3/tutorial/',
         "views": 40},
        {'title': 'How to Think like a Computer Scientist',
         'url': 'http://www.greenteapress.com/thinkpython/',
         "views": 20
         },
        {'title': 'Learn Python in 10 Minutes',
         'url': 'http://www.korokithakis.net/tutorials/python/',
         "views": 10}, ]

    django_pages = [
        {'title': 'Official Django Tutorial',
         'url': 'https://docs.djangoproject.com/en/2.1/intro/tutorial01/',
         "views": 40
         },
        {'title': 'Django Rocks',
         'url': 'http://www.djangorocks.com/',
         "views": 20
         },
        {'title': 'How to Tango with Django',
         'url': 'http://www.tangowithdjango.com/',
         "views": 10
         }]

    other_pages = [
        {'title': 'Bottle',
         'url': 'http://bottlepy.org/docs/dev/',
         "views": 40},
        {'title': 'Flask',
         'url': 'http://flask.pocoo.org',
         "views": 20}]

    # Diccionario de diccionarios
    cats = {'Python': [{'pages': python_pages}, {'views': 128}, {'likes': 64}],
            'Django': [{'pages': django_pages}, {'views': 128}, {'likes': 64}],
            'Other Frameworks': [{'pages': other_pages},
                                 {'views': 128}, {'likes': 64}]
            }

    # If you want to add more categories or pages,
    # add them to the dictionaries above.
    # The code below goes through the cats dictionary, then adds each category,
    # and then adds all the associated pages for that category.

    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data[int(1)]['views'], cat_data[int(2)]['likes'])
        for p in cat_data[int(0)]['pages']:
            add_page(c, p['title'], p['url'], p["views"])

    # Print out the categories we have added.
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print('- {0} - {1}'.format(str(c), str(p)))


def add_cat(name, views=0, likes=0):
    # we use get or create to avoid repetition of objects
    # if it does not exist, create it. In other case, return a reference to it

    # el 0 es porque nos devuelve el objeto creado (o encontrado).
    # El elemento 1 es un boolean de si ha creado o encontrado
    c = Category.objects.get_or_create(name=name, views=views, likes=likes)[0]
    c.views = views
    c.likes = likes
    c.save()
    print(c.slug)
    return c


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p


if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()
