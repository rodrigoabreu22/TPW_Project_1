from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from AmorCamisola.models import *
from AmorCamisola.models import User as DBUser


class CreateAccountForm(UserCreationForm):
    name = forms.CharField(label='Nome', max_length=100, required=True)
    username = forms.CharField(label='Nome de utilizador', max_length=100, required=True)
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'password1', 'password2')


class ProductForm(forms.Form):
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

class ProductQuery(forms.Form):
    name_query = forms.CharField(label='Search product name', max_length=50, required=False)
    user_query = forms.CharField(label='Search seller', max_length=50, required=False)

    # Dynamically load teams from the Product model
    teams = forms.ModelMultipleChoiceField(
        queryset=Product.objects.values_list('team', flat=True).distinct(),
        widget=forms.CheckboxSelectMultiple(),
        label='Teams',
        required=False
    )

    PRODUCT_TYPE_CHOICES = [
        ('Jersey', 'Jersey'),
        ('Boots', 'Boots'),
        ('Socks', 'Socks'),
        ('Shorts', 'Shorts'),
    ]
    product_types = forms.MultipleChoiceField(
        choices=PRODUCT_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        label='Product Types',
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


