from django import forms
from django.contrib.auth.models import User

from datamodel.models import UserProfile


class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'placeholder': 'Minimum 8 characters'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    repeat_password = forms.CharField(widget=forms.PasswordInput, required=True)

    # REVISAR: Hacer una expresion regular chula que te compruebe que la contraseña sea minimo 8,
    # incluya alguna mayusucula, minuscula, y simbolo, y que el usuario por ejemplo que contenga
    # solo letras (mayus o minus).
    def is_valid(self):
        user = super(self).get("username")
        if len(user) >= 8 and self.password == self.repeat_password and len(self.password) >= 8:
            return True
        return False

    class Meta:
        model = User
        fields = ('username', 'password', 'repeat_password')


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
