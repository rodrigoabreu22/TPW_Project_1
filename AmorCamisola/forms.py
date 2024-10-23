from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from AmorCamisola.models import *


class CreateAccountForm(forms.Form):
    firstname = forms.CharField(label='Nome', max_length=100, required=True)
    lastname = forms.CharField(label='Último nome', max_length=100, required=True)
    username = forms.CharField(label='Nome de utilizador', max_length=100, required=True)
    email = forms.EmailField(label='Email', required=True)
    cc = forms.CharField(label='Número cartão de cidadão', required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)



class ProductForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'equipa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control'}),
            'equipa': forms.TextInput(attrs={'class': 'form-control'}),
        }

