# Generated by Django 2.2.5 on 2019-10-07 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0004_auto_20191007_0045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
