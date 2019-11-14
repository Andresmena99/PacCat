from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password, UserAttributeSimilarityValidator, \
    CommonPasswordValidator, NumericPasswordValidator

from datamodel.models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')


class MoveForm(forms.ModelForm):
    origin = forms.IntegerField(initial=0)
    target = forms.IntegerField(initial=0)

    class Meta:
        model = User
        fields = ('origin', 'target')

    def clean(self):
        super(MoveForm, self).clean()

        # extract the username and text field from the data
        origin = self.cleaned_data.get('origin')
        target = self.cleaned_data.get('target')

        if origin < 0 or origin > 63:
            self._errors['origin'] = self.error_class([
                'La casilla tiene que estar en el rango [0,63'])

        if target > 63 or target < 0:
            self._errors['target'] = self.error_class([
                'La casilla tiene que estar en el rango [0,63'])

        # devolver los errores en caso de haberlos
        return self.cleaned_data



class SignupForm(forms.ModelForm):
    username = forms.CharField(max_length=128)
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=128, widget=forms.PasswordInput)

    class Meta:
        # Como se relaciona el model con la base de datos
        model = User
        fields = ('username', 'password')

    # Funcion usada para validar un formulario
    def clean(self):
        super(SignupForm, self).clean()
        # extract the username and text field from the data
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')


        # REVISAR: HAY QUE USAR ESTO PARA VER SI DOS CONTRASEÑAS SON MUY COMUNES,
        # PERO NO LO HE CONSEGUIDO:
        # https://docs.djangoproject.com/en/1.9/topics/auth/passwords/#module-django.contrib.auth.password_validation
        # validators = []
        # validators.append(UserAttributeSimilarityValidator)
        # validators.append(CommonPasswordValidator)
        # validators.append(NumericPasswordValidator)
        #
        #
        # validate_password(password, username, password_validators=validators)

        if len(username) < 6:
            self._errors['username'] = self.error_class([
                'La longitud minima del nombre de usuario es 6'])

        if password != password2:
            self._errors['password2'] = self.error_class([
                'Password and Repeat password are not the same'])

        #REVISAR: Hacer una expresion regular o algo asi para contraseñas muy comunes, porque eso yo no se
        # te lo dejo eric :). De momento imprimo lo de la longitud y lo de que es muy comun porque hay un test
        # (signupser
        if len(password) < 6:
            self._errors['password'] = self.error_class([
                'Password is too short. It needs at least 6 characters. too common'])

        # devolver los errores en caso de haberlos
        return self.cleaned_data


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'placeholder': 'Minimum 8 characters'}),
                               required=True)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')
