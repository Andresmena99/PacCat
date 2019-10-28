from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
import datetime

class User(models.Model):
    name = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class GameStatus(Enum):
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2

    @class_method
    def get_values(cls):
        return (
            (cls.CREATED, 'Created'),
            (cls.ACTIVE, 'Active'),
            (cls.FINISHED, 'Finished'))


class Game(models.Model):
    cat_user = models.ForeignKey(User, on_delete=models.CASCADE)
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE)

    cat1 = models.IntegerField(blank=False, null=False)
    cat2 = models.IntegerField(blank=False, null=False)
    cat3 = models.IntegerField(blank=False, null=False)
    cat4 = models.IntegerField(blank=False, null=False)
    mouse = models.IntegerField(blank=False, null=False)
    #REVISAR
    status = models.CharField(choices = GameStatus.get_values(), status = GameStatus, blank=False, null=False)

    def save(self, *args, **kwargs):
        if 0<=cat1<=63 and 0<=cat2<=63 and 0<=cat3<=63 and 0<=cat4<=63 and 0<=mouse<=63:
            if (status != 'Created' and status != 'Active' and status != 'Finished'):
                super(Game, self).save(*args, **kwargs)
        else:
            #REVISAR
            raise ValidationError("Casillas no válidas o status no válido")



    def __str__(self):
        return self.name



class Move(models.Model):
    origin = models.IntegerField(blank=False, null=False)
    target = models.IntegerField(blank=False, null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default = datetime.now, blank=False, null=False)

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
