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
    CATEGORIES= [
        ('1', 'Camisola'),
        ('2', 'Calções'),
        ('3', 'Meias'),
        ('4', 'Chuteira'),
    ]

    name = forms.CharField(label='Nome', max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label='Descrição', required=True, widget=forms.Textarea(attrs={'class': 'form-control'}))
    price = forms.DecimalField(label='Preço', required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    team = forms.CharField(label='Equipa', max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.ChoiceField(label='Categoria', choices=CATEGORIES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    image = forms.ImageField(label='Imagem do Produto', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))
    size = forms.CharField(label='Tamanho', widget=forms.TextInput(attrs={'class': 'form-control'}))

