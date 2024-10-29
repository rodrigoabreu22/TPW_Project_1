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
        model = Product
        fields = ['name', 'description', 'price', 'team']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control'}),
            'equipa': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProductQuery(forms.Form):
    name_query = forms.CharField(label='Search product name', max_length=50, required=False)
    user_query = forms.CharField(label='Search seller', max_length=50, required=False)

    # Dynamically load teams from the Product model
    teams = forms.MultipleChoiceField(
        label="Teams",
        choices=[(team, team) for team in Product.objects.values_list("team", flat=True).distinct() if team],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    PRODUCT_TYPE_CHOICES = [
        ('Jersey', 'Jersey'),
        ('Boots', 'Boots'),
        ('Socks', 'Socks'),
        ('Shorts', 'Shorts'),
    ]
    product_types = forms.MultipleChoiceField(
        label='Product Types',
        choices=PRODUCT_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    # Price range fields
    min_price = forms.DecimalField(
        label='Minimum Price',
        max_digits=10,
        decimal_places=2,
        required=False
    )
    max_price = forms.DecimalField(
        label='Maximum Price',
        max_digits=10,
        decimal_places=2,
        required=False
    )

    # Sorting options
    SORT_CHOICES = [
        ('price_asc', 'Price (Low to High)'),
        ('price_desc', 'Price (High to Low)'),
        ('name_asc', 'Product Name (A to Z)'),
        ('name_desc', 'Product Name (Z to A)'),
        ('seller_asc', 'Seller Name (A to Z)'),
        ('seller_desc', 'Seller Name (Z to A)'),
    ]
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        label='Sort By',
        required=False
    )


