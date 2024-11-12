from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

CLOTHES_CHOICES = (
    ("XS", "XS"),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL")
)

BOOTS_CHOICES = (
    (30, 30),
    (31, 31),
    (32, 32),
    (33, 33),
    (34, 34),
    (35, 35),
    (36, 36),
    (37, 37),
    (38, 38),
    (39, 39),
    (40, 40),
    (41, 41),
    (42, 42),
    (43, 43),
    (44, 44),
    (45, 45),
    (46, 46),
    (47, 47),
    (48, 48)
)

PAYMENT_METHOD_CHOICES = (
    ('store_credit', 'Saldo da loja'),
    ('transfer', 'Transferência bancária'),
    ('in_person', 'Em pessoa'),
)

DELIVERY_METHOD_CHOICES = (
    ('shipment', 'Envio remoto'),
    ('in_person', 'Em pessoa'),
)

OFFER_STATUS = (
    ('in_progress', 'Em progresso'),
    ('accepted', 'Aceite'),
    ('rejected', 'Rejeitado')
)

phone_validator = RegexValidator(regex=r'^\d{9}$', message="Phone number must be exactly 9 digits.")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=50)

    phone = models.CharField(max_length=9,unique=True,null=False,blank=False,validators=[phone_validator])
    image = models.FileField()
    wallet = models.DecimalField(max_digits=50, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username

    def update_image(self, file):
        self.image.storage.delete(self.image.name)
        self.image = file


class Following(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')

    def __str__(self):
        return self.following.username + " follows " + self.followed.username



class Product(models.Model):
    name = models.CharField(max_length=50)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='produtos/')
    price = models.DecimalField(max_digits=50, decimal_places=2)
    team = models.CharField(max_length=50, null=True)
    description = models.TextField()
    sold = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ReportOptions(models.TextChoices):
    INAPPROPRIATE = 'IN', 'Conteúdo inapropriado'
    FRAUD = 'FR', 'Fraude'
    OTHER = 'OT', 'Outro'

class Report(models.Model):
    sent_by = models.ForeignKey(User, related_name='reports_sent', on_delete=models.CASCADE)
    reporting = models.ForeignKey(User, related_name='reports_received', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    reasons = models.CharField(max_length=2, choices=ReportOptions.choices)
    description = models.TextField(max_length=500)

    def __str__(self):
        target = f"Product {self.product.name}" if self.product else f"User {self.reporting.username}"
        return f"{target} reported by {self.sent_by.username}"

    def clean(self):
        if not self.reporting and not self.product:
            raise ValidationError("You must report either a user or a product.")
        if self.reporting and self.product:
            raise ValidationError("A report cannot target both a user and a product.")

class Favorite(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"{self.user.username}'s Favorites"

class Jersey(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, choices=CLOTHES_CHOICES)

    def __str__(self):
        return self.product.__str__()


class Shorts(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, choices=CLOTHES_CHOICES)

    def __str__(self):
        return self.product.__str__()


class Socks(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, choices=CLOTHES_CHOICES)

    def __str__(self):
        return self.product.__str__()


class Boots(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    size = models.IntegerField(choices=BOOTS_CHOICES)

    def __str__(self):
        return self.product.__str__()


class Offer(models.Model):
    buyer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='buyer')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    delivery_method = models.CharField(max_length=50, choices=DELIVERY_METHOD_CHOICES)
    address = models.CharField(max_length=50)
    sent_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_by')
    offer_status = models.CharField(max_length=50, choices=OFFER_STATUS, default='in_progress')
    delivered = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

