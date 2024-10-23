from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from models import *


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

class ProductForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'equipa', 'categoria']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control'}),
            'equipa': forms.TextInput(attrs={'class': 'form-control'}, required=False),
        }

