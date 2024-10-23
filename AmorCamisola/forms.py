from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreateAccountForm(UserCreationForm):
    firstname = forms.CharField(label='Nome', max_length=100, required=True)
    lastname = forms.CharField(label='Nome', max_length=100, required=True)
    username = forms.CharField(label='Nome de utilizador', max_length=100, required=True)
    email = forms.EmailField(label='Email', required=True)
    cc = forms.IntegerField(label='Número cartão de cidadão', required=True)
    telemovel = forms.CharField(label='Telefone', max_length=9, required=True)

    class Meta:
        model = User
        fields = ('firstname', 'lastname', 'username', 'email', 'cc', 'telemovel', 'password1', 'password2')