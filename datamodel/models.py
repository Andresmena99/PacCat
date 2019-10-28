from django.contrib.auth.models import User
from django.db import models
from enum import IntEnum
from django.template.defaultfilters import slugify
import datetime

class GameStatus(IntEnum):
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2

    @classmethod
    def get_values(cls):
        return (
            (cls.CREATED, 'Created'),
            (cls.ACTIVE, 'Active'),
            (cls.FINISHED, 'Finished'))


class Game(models.Model):
    cat_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games_as_cat")
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="games_as_mouse")

    cat1 = models.IntegerField(blank=False, null=False)
    cat2 = models.IntegerField(blank=False, null=False)
    cat3 = models.IntegerField(blank=False, null=False)
    cat4 = models.IntegerField(blank=False, null=False)
    mouse = models.IntegerField(blank=False, null=False)
    cat_turn = models.BooleanField(blank=False, null=False)
    #REVISAR
    status = models.IntegerField(choices=GameStatus.get_values(), default=GameStatus.CREATED)

    def save(self, *args, **kwargs):
        print("Status "+self.status)
        if (self.status == GameStatus.CREATED):
            self.cat1 = 0
            self.cat2 = 2
            self.cat3 = 4
            self.cat4 = 6
            self.mouse = 59
            self.cat_turn = True
            self.status = GameStatus.ACTIVE

        # elif (status == GameStatus.ACTIVE):
        #     if 0<=cat1<=63 and 0<=cat2<=63 and 0<=cat3<=63 and 0<=cat4<=63 and 0<=mouse<=63:
        #     #if not (status != 'Created' and status != 'Active' and status != 'Finished'):
        #
        #     else:
        #         #REVISAR
        #         raise ValidationError("Casillas no válidas o status no válido")
        # else:
        #     pass

        super(Game, self).save(*args, **kwargs)

    def __str__(self):
        return self.name



class Move(models.Model):
    origin = models.IntegerField(blank=False, null=False)
    target = models.IntegerField(blank=False, null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        return self.name










class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username
