from django import forms
from django.contrib.auth.forms import UserCreationForm

from AmorCamisola.models import *


class CreateAccountForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        required=True,
        error_messages={
            'required': 'O campo \'email\' tem de ser preenchido.',
            'invalid': 'Insira um endereço de email válido',
        }
    )
    first_name = forms.CharField(
        label='First Name',
        max_length=30,
        required=True,
        error_messages={
            'required': 'O campo \'Nome\' tem de ser preenchido.',
            'max_length': 'O nome não pode exceder 30 caracteres.',
        }
    )
    last_name = forms.CharField(
        label='Last Name',
        max_length=30,
        required=True,
        error_messages={
            'required': 'O campo \'Apelido\' tem de ser preenchido.',
            'max_length': 'O apelido não pode exceder 30 caracteres.',
        }
    )
    address = forms.CharField(
        label='Address',
        max_length=50,
        required=True,
        error_messages={
            'max_length': 'A morada não pode exceder 50 caracteres.',
            'required': 'O campo \'Morada\' tem de ser preenchido.',
        }
    )
    phone = forms.CharField(
        label='Phone',
        required=True,
        validators=[RegexValidator(regex=r'^\d{9}$')],
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 9876543210'}),
        error_messages={
            'required': 'O campo \'Telefone\' tem de ser preenchido.',
            'invalid': 'Insira um número de telefone válido (9 dígitos)',
        }
    )

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
            UserProfile.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone']
            )
        return user

class UploadProfilePicture(forms.Form):
    image = forms.FileField(widget=forms.FileInput(
        attrs={'class': 'form-control',
               'id': 'image',
               'name': 'input_file',
               'accept': 'image/*'
               }
    ))

class UpdatePassword(forms. Form):
    new = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class UpdateUser(forms.Form):
    first_name = forms.CharField(label='Primeiro Nome', max_length=30, required=True)
    last_name = forms.CharField(label='Último Nome', max_length=30, required=True)
    username = forms.CharField(label='Nome de Utilizador', max_length=30, required=True)
    email = forms.EmailField(label='Email', required=True)

class UpdateProfile(forms.Form):
    address = forms.CharField(label='Address', max_length=50)
    phone = forms.CharField(label='Phone', required=True)


class ProductForm(forms.Form):
    CATEGORIES = [
        ('1', 'Camisola'),
        ('2', 'Calções'),
        ('3', 'Meias'),
        ('4', 'Chuteira'),
    ]

    SIZE_CHOICES = [
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'),
        ('30', '30'), ('31', '31'), ('32', '32'), ('33', '33'), ('34', '34'), ('35', '35'),
        ('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'),
        ('42', '42'), ('43', '43'), ('44', '44'), ('45', '45'), ('46', '46'), ('47', '47'), ('48', '48')
    ]

    name = forms.CharField(label='Nome', max_length=255, required=True)
    description = forms.CharField(label='Descrição', required=True, widget=forms.Textarea)
    price = forms.DecimalField(label='Preço', required=True, min_value=0.00)
    team = forms.CharField(label='Equipa', max_length=255, required=False)
    category = forms.ChoiceField(label='Categoria', choices=CATEGORIES, required=True)
    size = forms.ChoiceField(label='Tamanho', choices=SIZE_CHOICES, required=True)
    image = forms.ImageField(label='Imagem do Produto', required=True)


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
        if not userProfile is None:
            self.fields['custom_address'].value = userProfile.address



class ProductQuery(forms.Form):
    name_query = forms.CharField(label='Search product name', max_length=50, required=False)
    user_query = forms.CharField(label='Search seller', max_length=50, required=False)

    teams = forms.MultipleChoiceField(
        label="Teams",
        choices=[],
        #choices=[(team, team) for team in Product.objects.values_list("team", flat=True).distinct() if team],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    PRODUCT_TYPE_CHOICES = [
        ('Camisola', 'Camisola'),
        ('Chuteiras', 'Chuteiras'),
        ('Meias', 'Meias'),
        ('Calções', 'Calções'),
    ]
    product_types = forms.MultipleChoiceField(
        label='Product Types',
        choices=PRODUCT_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

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

    SORT_CHOICES = [
        ('price_asc', 'Preço (Menor a Maior)'),
        ('price_desc', 'Preço (Maior a Menor)'),
        ('name_asc', 'Nome (A a Z)'),
        ('name_desc', 'Nome (Z a A)'),
        ('seller_asc', 'Vendedor (A a Z)'),
        ('seller_desc', 'Vendedor (Z a A)'),
    ]
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        label='Sort By',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teams'].choices = [
            (team, team) for team in Product.objects.filter(sold=False).values_list("team", flat=True).distinct() if
            team
        ]

class FavoriteForm(forms.Form):
    favorite_product_id = forms.IntegerField(required=True)

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reasons', 'description']
        labels = {
            'reasons': 'Motivo',
            'description': 'Descrição'
        }
        widgets = {
            'reasons': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SearchUserForm(forms.Form):
    query = forms.CharField(label='Procurar utilizador', max_length=50, required=False)

class DepositForm(forms.Form):
    deposit_amount = forms.DecimalField(label="Quantia a Depositar", max_digits=10, decimal_places=2, min_value=0.01)

class WithdrawalForm(forms.Form):
    withdrawal_amount = forms.DecimalField(label="Quantia a Levantar", max_digits=10, decimal_places=2, min_value=0.01)