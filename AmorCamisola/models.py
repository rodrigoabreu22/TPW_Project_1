import uuid
from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

CLOTHES_CHOICES = (
    ("XS", "XS"),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL")
)

SOCKS_CHOICES = (
    ("S", "S"),
    ("M", "M"),
    ("L", "L")
)

BOOTS_CHOICES = (
    (36, 36),
    (36.5, 36.5),
    (37, 37),
    (37.5, 37.5),
    (38, 38),
    (38.5, 38.5),
    (39, 39),
    (39.5, 39.5),
    (40, 40),
    (40.5, 40.5),
    (41, 41),
    (41.5, 41.5),
    (42, 42),
    (42.5, 42.5),
    (43, 43),
    (43.5, 43.5),
    (44, 44),
    (44.5, 44.5),
    (45, 45),
    (45.5, 45.5),
    (46, 46),
    (46.5, 46.5),
    (47, 47)
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

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cc = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    phone = PhoneNumberField(unique=True, null=False, blank=False)
    image = models.ImageField(upload_to='media/produtos')
    wallet = models.DecimalField(max_digits=50, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username


class Following(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')

    def __str__(self):
        return self.following.username + " follows " + self.followed.username


class Moderator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    name = models.CharField(max_length=50)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    # compra = models.ForeignKey(Purchase) isto seria caso tenhamos historico de compras
    image = models.ImageField(upload_to='produtos/')
    price = models.DecimalField(max_digits=5, decimal_places=2)
    team = models.CharField(max_length=50, null=True)
    description = models.TextField()
    sold = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Favorite(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username + " favorites " + self.product.name

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
    size = models.CharField(max_length=50, choices=SOCKS_CHOICES)

    def __str__(self):
        return self.product.__str__()


class Boots(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    size = models.DecimalField(max_digits=50, decimal_places=2, choices=BOOTS_CHOICES)

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



"""Deixar para o fim!!!
class Purchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(User, related_name='buyer', on_delete=models.CASCADE, primary_key=True)
    seller = models.ForeignKey(User, related_name='seller', on_delete=models.CASCADE, primary_key=True)
    products = models.ManyToOneField(Produto)


   def __str__(self):
        return self.buyer.username + " made a purchase with id " + self.id 

class PurchaseItem(models.Model):
    purchase_id = models.ForeignKey(Purchase, related_name='purchase', on_delete=models.CASCADE, primary_key=True)
    product_id = models.ForeignKey(Product, related_name='product', on_delete=models.CASCADE, primary_key=True)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return purchase_id.id + ' contains product with id ' + product_id.nome
"""



