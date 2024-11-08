from django import forms
from django.contrib.auth.forms import UserCreationForm
from pkg_resources import require

from AmorCamisola.models import *
from phonenumber_field.formfields import PhoneNumberField


class CreateAccountForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='First Name', max_length=30, required=True)
    last_name = forms.CharField(label='Last Name', max_length=30, required=True)
    cc = forms.CharField(label='CC', max_length=50)
    address = forms.CharField(label='Address', max_length=50)
    phone = PhoneNumberField(label='Phone', required=True)


    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            # Save additional fields in UserProfile
            UserProfile.objects.create(
                user=user,
                cc=self.cleaned_data['cc'],
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone']
            )
        return user


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

class ListingOffer(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('store_credit', 'Saldo da loja'),
        ('transfer', 'Transferência bancária'),
        ('in_person', 'Em pessoa'),
    ]

    DELIVERY_METHOD_CHOICES = [
        ('shipment', 'Envio remoto'),
        ('in_person', 'Em pessoa'),
    ]

    ADDRESS_CHOICES = [
        ('profile_address', 'Usar localização do perfil'),
        ('custom_address', 'Inserir localização'),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        label="Método de Pagamento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    delivery_method = forms.ChoiceField(
        choices=DELIVERY_METHOD_CHOICES,
        label="Método de Entrega",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    address_choice = forms.ChoiceField(
        choices=ADDRESS_CHOICES,
        label="Localização da Entrega",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    custom_address = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter custom address'}),
    )

    value = forms.DecimalField(
        label="Proposta de valor",
        max_digits=50,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, userProfile, product, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not product is None:
            self.fields['value'].initial = product.price
        else:
            self.fields['value'].initial = 0
        self.fields['payment_method'].initial = 'store_credit'
        self.fields['delivery_method'].initial = 'transfer'
        self.fields['address_choice'].initial = 'profile_address'
        self.fields['custom_address'].value = userProfile.address



class ProductQuery(forms.Form):
    name_query = forms.CharField(label='Search product name', max_length=50, required=False)
    user_query = forms.CharField(label='Search seller', max_length=50, required=False)

    # Dynamically load teams from the Product model
    teams = forms.MultipleChoiceField(
        label="Teams",
        choices=[],
        #choices=[(team, team) for team in Product.objects.values_list("team", flat=True).distinct() if team],
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define os choices de 'teams' dinamicamente
        self.fields['teams'].choices = [
            (team, team) for team in Product.objects.values_list("team", flat=True).distinct() if team
        ]

class SearchUserForm(forms.Form):
    query = forms.CharField(label='Procurar utilizador', max_length=50, required=False)


