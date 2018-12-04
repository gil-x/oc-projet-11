from django import forms
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur ", max_length=30)
    password = forms.CharField(label="Mot de passe ", widget=forms.PasswordInput)

class CreateUser(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur ", max_length=30)
    email = forms.EmailField(label="Email ", max_length=30)
    password = forms.CharField(label="Mot de passe ", widget=forms.PasswordInput)
    password_verification = forms.CharField(label="Mot de passe (vérification) ", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(CreateUser, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password_verification = cleaned_data.get('password_verification')

        if password and password_verification:
            if password != password_verification:
                raise forms.ValidationError(
                    "Les deux mots de passe sont différents."
                )

        return cleaned_data

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    password2 = forms.CharField(label="Mot de passe (vérification)", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    json_file = forms.FileField()