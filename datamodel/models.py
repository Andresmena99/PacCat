from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from enum import IntEnum
from django.template.defaultfilters import slugify
import datetime
from datamodel import constants

CAT1POS = 0
CAT2POS = 2
CAT3POS = 4
CAT4POS = 6
MOUSEPOS = 59

TABLERO = {0: (1, 1), 1: (1, 2), 2: (1, 3), 3: (1, 4), 4: (1, 5), 5: (1, 6),
           6: (1, 7), 7: (1, 8), 8: (2, 1), 9: (2, 2),
           10: (2, 3), 11: (2, 4), 12: (2, 5), 13: (2, 6), 14: (2, 7),
           15: (2, 8), 16: (3, 1), 17: (3, 2), 18: (3, 3),
           19: (3, 4), 20: (3, 5), 21: (3, 6), 22: (3, 7), 23: (3, 8),
           24: (4, 1), 25: (4, 2), 26: (4, 3), 27: (4, 4),
           28: (4, 5), 29: (4, 6), 30: (4, 7), 31: (4, 8), 32: (5, 1),
           33: (5, 2), 34: (5, 3), 35: (5, 4), 36: (5, 5),
           37: (5, 6), 38: (5, 7), 39: (5, 8), 40: (6, 1), 41: (6, 2),
           42: (6, 3), 43: (6, 4), 44: (6, 5), 45: (6, 6),
           46: (6, 7), 47: (6, 8), 48: (7, 1), 49: (7, 2), 50: (7, 3),
           51: (7, 4), 52: (7, 5), 53: (7, 6), 54: (7, 7),
           55: (7, 8), 56: (8, 1), 57: (8, 2), 58: (8, 3), 59: (8, 4),
           60: (8, 5), 61: (8, 6), 62: (8, 7), 63: (8, 8)
           }

WHITE_SPOTS = [0, 2, 4, 6, 9, 11, 13, 15, 16, 18, 20, 22, 25, 27, 29, 31, 32,
               34, 36, 38, 41, 43, 45, 47, 48, 50, 52,
               54, 57, 59, 61, 63]


# Resto de dividir el numero de la casilla entre 8, y tiene que ser par (para casilla blanca), impar para las otras

def validate_position(value):
    if not (Game.MIN_CELL <= value <= Game.MAX_CELL):
        print("SOY YO")
        raise ValidationError(constants.MSG_ERROR_MOVE)

    if (value // 8) % 2 == 0:
        if value % 2 != 0:
            raise ValidationError(constants.MSG_ERROR_INVALID_CELL)
    else:
        if value % 2 == 0:
            raise ValidationError(constants.MSG_ERROR_INVALID_CELL)


def valid_move(cat_turn, origin, target):
    validate_position(target)
    validate_position(origin)

    print("----- valid_move")
    print(origin)
    print(target)

    x_ori = origin // 8 + 1
    y_ori = origin % 8 + 1

    x_tar = target // 8 + 1
    y_tar = target % 8 + 1

    print(x_ori)
    print(y_ori)
    print(x_tar)
    print(y_tar)

    if cat_turn:
        if x_tar != x_ori + 1:
            print("-1")
            raise ValidationError(constants.MSG_ERROR_MOVE)
        elif y_tar != y_ori + 1 and y_tar != y_ori - 1:
            print("-2")
            raise ValidationError(constants.MSG_ERROR_MOVE)
    else:
        if x_tar != x_ori + 1 and x_tar != x_ori - 1:
            print("-3")
            raise ValidationError(constants.MSG_ERROR_MOVE)
        elif y_tar != y_ori + 1 and y_tar != y_ori - 1:
            print("-4")
            raise ValidationError(constants.MSG_ERROR_MOVE)


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
    MIN_CELL = 0
    MAX_CELL = 63

    cat_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name="games_as_cat")
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                   blank=True, related_name="games_as_mouse")

    cat1 = models.IntegerField(default=CAT1POS, blank=False, null=False,
                               validators=[validate_position])
    cat2 = models.IntegerField(default=CAT2POS, blank=False, null=False,
                               validators=[validate_position])
    cat3 = models.IntegerField(default=CAT3POS, blank=False, null=False,
                               validators=[validate_position])
    cat4 = models.IntegerField(default=CAT4POS, blank=False, null=False,
                               validators=[validate_position])
    mouse = models.IntegerField(default=MOUSEPOS, blank=False, null=False,
                                validators=[validate_position])
    cat_turn = models.BooleanField(default=True, blank=False, null=False)

    # REVISAR comentar en la memoria
    status = models.IntegerField(default=GameStatus.CREATED)

    def save(self, *args, **kwargs):
        validate_position(self.cat1)
        validate_position(self.cat2)
        validate_position(self.cat3)
        validate_position(self.cat4)
        validate_position(self.mouse)

        if self.status == GameStatus.CREATED:
            self.cat1 = CAT1POS
            self.cat2 = CAT2POS
            self.cat3 = CAT3POS
            self.cat4 = CAT4POS
            self.mouse = MOUSEPOS
            self.cat_turn = True

        # Cuando nos metan al mouse, pasamos a estado activo
        if self.mouse_user and self.status == GameStatus.CREATED:
            self.status = GameStatus.ACTIVE

        super(Game, self).save(*args, **kwargs)

    def __str__(self):
        response = "(" + str(self.id) + ", "
        if self.status == GameStatus.ACTIVE:
            response += "Active)\t"
        elif self.status == GameStatus.FINISHED:
            response += "Finished)\t"

        elif self.status == GameStatus.CREATED:
            response += "Created)\t"

        response += "Cat [X] " if self.cat_turn else "Cat [ ] "

        response += str(self.cat_user) + "(" + str(self.cat1) \
                    + ", " + str(self.cat2) + ", " + str(self.cat3) \
                    + ", " + str(self.cat4) + ")"
        if self.mouse_user:
            response += " --- Mouse "
            response += "[X] " if not self.cat_turn else "[ ] "
            response += str(self.mouse_user) + "(" + str(self.mouse) + ")"

        return response


class Move(models.Model):
    origin = models.IntegerField(blank=False, null=False)
    target = models.IntegerField(blank=False, null=False)
    game = models.ForeignKey(Game,
                             on_delete=models.CASCADE,
                             related_name='moves')
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        # REVISAR no sabemos como imprimir
        return "origin: " + str(self.origin) + "\nTarget: " + str(self.target)


    def save(self, *args, **kwargs):

        if self.game.status == GameStatus.CREATED or self.game.status == GameStatus.FINISHED:
            raise ValidationError(constants.MSG_ERROR_MOVE)


        valid_move(self.game.cat_turn, self.origin, self.target)

        if self.player == self.game.cat_user:
            if self.game.cat_turn:
                if self.game.cat1 == self.origin:
                    self.game.cat1 = self.target
                    self.game.cat_turn = False

                elif self.game.cat2 == self.origin:
                    self.game.cat2 = self.target
                    self.game.cat_turn = False

                elif self.game.cat3 == self.origin:
                    self.game.cat3 = self.target
                    self.game.cat_turn = False

                elif self.game.cat4 == self.origin:
                    self.game.cat4= self.target
                    self.game.cat_turn = False
                else:
                    print("este1")
                    raise ValidationError(constants.MSG_ERROR_MOVE)
            else:
                print("este2")
                raise ValidationError(constants.MSG_ERROR_MOVE)
        elif self.player == self.game.mouse_user:
            if not self.game.cat_turn:
                if self.game.mouse == self.origin:
                    self.game.mouse = self.target
                    self.game.cat_turn = True
            else:
                print("este3")
                raise ValidationError(constants.MSG_ERROR_MOVE)
        else:
            print("este4")
            raise ValidationError(constants.MSG_ERROR_MOVE)

        super(Move, self).save(*args, **kwargs)


class SingletonModel(models.Model): # Revisar este copypaste de google
    """Singleton Django Model"""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Save object to the database. Removes all other entries if there
        are any.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load object from the database. Failing that, create a new empty
        (default) instance of the object and return it (without saving it
        to the database).
        """

        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class CounterManager(models.Manager):
    def get_current_value(self):
        return Counter.load().value

    def inc(self):
        counter = Counter.load()
        counter.value += 1
        super(Counter, counter).save()
        return self.get_current_value()

    def create(self, *args, **kwargs):
        raise ValidationError(constants.MSG_ERROR_NEW_COUNTER)


class Counter(SingletonModel):
    value = models.IntegerField(default=0, blank=False, null=False)
    objects = CounterManager()

    def save(self, *args, **kwargs):
        raise ValidationError(constants.MSG_ERROR_NEW_COUNTER)



class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username
