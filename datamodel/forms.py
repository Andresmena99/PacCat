# REVISAR creo que hay que borrar esto
from django import forms

from datamodel.models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
