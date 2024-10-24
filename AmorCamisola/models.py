import uuid
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

CLOTHES_CHOICES = ((0, "XS"), (1, "S"), (2, "M"), (3, "L"), (4, "XL"), (5, "XXL"))
SOCKS_CHOICES = ((0, "S"), (1, "M"), (2, "L"))
BOOTS_CHOICES = ((0, 36), (1, 37), (2, 38), (3, 39), (4, 40), (5, 41), (6, 42), (7, 43), (8, 44), (9, 45), (10, 46), (11, 47))



class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    cc = models.CharField(max_length=50, primary_key=True)
    address = models.CharField(max_length=50)
    phone = PhoneNumberField(unique=True, null=False, blank=False)
    wallet = models.DecimalField(max_digits=50, decimal_places=2, default=0)

    def __str__(self):
        return self.username


class Following(models.Model):
    following = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="follower")
    followed = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="followed")

    def __str__(self):
        return self.following.username + " follows " + self.followed.username


class Moderator(models.Model):
    cc = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    admin = models.BooleanField(default=False)

    def __str__(self):
        return self.cc


class Product(models.Model):
    name = models.CharField(max_length=50)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    # compra = models.ForeignKey(Purchase) isto seria caso tenhamos historico de compras
    image = models.ImageField(upload_to='produtos')
    price = models.DecimalField(max_digits=5, decimal_places=2)
    team = models.CharField(max_length=50, null=True)
    description = models.TextField()
    sold = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    def __str__(self):
        return self.user + " favorites " + self.product

class Jersey(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, choices=CLOTHES_CHOICES)

    def __str__(self):
        return self.product


class Shorts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, choices=CLOTHES_CHOICES)

    def __str__(self):
        return self.product


class Socks(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, choices=SOCKS_CHOICES)

    def __str__(self):
        return self.product


class Boots(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.DecimalField(max_digits=50, decimal_places=2, choices=BOOTS_CHOICES)

    def __str__(self):
        return self.product


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



