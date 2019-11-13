from django import forms
from django.contrib.auth.models import User

from datamodel.models import UserProfile

class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'placeholder': 'Minimum 8 characters'}),
                               required=True)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')


class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=128)
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)
    repeat_password = forms.CharField(max_length=128, widget=forms.PasswordInput)

    class Meta:
        # Como se relaciona el model con la base de datos
        model = User
        fields = ('username', 'password', 'repeat_password')

    # Funcion usada para validar un formulario
    def clean(self):
        super(RegisterForm, self).clean()

        # extract the username and text field from the data
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        password_repeat = self.cleaned_data.get('repeat_password')

        # Condiciones que tienen que cumplirse en el formulario
        # REVISAR: Hacer una expresion regular chula que te compruebe que la contraseña sea minimo 8,
        # incluya alguna mayusucula, minuscula, y simbolo, y que el usuario por ejemplo que contenga
        # solo letras (mayus o minus).
        if len(username) < 6:
            self._errors['username'] = self.error_class([
                'La longitud minima del nombre de usuario es 6'])

        if password != password_repeat:
            self._errors['repeat_password'] = self.error_class([
                'Las contraseñas no coinciden'])

        if len(password) < 6:
            self._errors['password'] = self.error_class([
                'Las contraseña tienen que tener por lo menos 6 caracteres'])

        # devolver los errores en caso de haberlos
        return self.cleaned_data
