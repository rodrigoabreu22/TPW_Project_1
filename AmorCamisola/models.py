import uuid
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

CLOTHES_CHOICES = ((0, "XS"), (1, "S"), (2, "M"), (3, "L"), (4, "XL"), (5, "XXL"))
SOCKS_CHOICES = ((0, "S"), (1, "M"), (2, "L"))
BOOTS_CHOICES = ((0, 36), (1, 36.5), (2, 37), (3, 37.5), (4, 38), (5, 38.5), (6, 39), (7, 39.5), (8, 40), (9, 40.5), (10, 41), (11, 41.5), (12, 42), (13, 42.5), (14, 43), (15, 43.5), (16, 44), (17, 44.5), (18, 45), (19, 45.5), (20, 46), (21, 46.5), (22, 47))



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


class Moderador(models.Model):
    id = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    admin = models.BooleanField(default=False)


class Produto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=50)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    # compra = models.ForeignKey(Purchase) isto seria caso tenhamos historico de compras
    imagem = models.ImageField(upload_to='produtos')
    preco = models.DecimalField(max_digits=5, decimal_places=2)
    equipa = models.CharField(max_length=50)
    descricao = models.TextField()

    def __str__(self):
        return self.nome

class Favorite(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Produto, on_delete=models.CASCADE)
    def __str__(self):
        return self.userId.username + " favorites " + self.product.nome

class Camisola(models.Model):
    id = models.ForeignKey(Produto, on_delete=models.CASCADE, primary_key=True)
    tamanho = models.CharField(max_length=50, choices=CLOTHES_CHOICES)

    def __str__(self):
        return self.id.nome


class Calcoes(models.Model):

    id = models.ForeignKey(Produto, on_delete=models.CASCADE, primary_key=True)
    tamanho = models.CharField(max_length=50, choices=CLOTHES_CHOICES)

    def __str__(self):
        return self.id.nome


class Meias(models.Model):
    id = models.ForeignKey(Produto, on_delete=models.CASCADE, primary_key=True)
    tamanho = models.CharField(max_length=50, choices=SOCKS_CHOICES)

    def __str__(self):
        return self.id.nome


class Chuteiras(models.Model):
    id = models.ForeignKey(Produto, on_delete=models.CASCADE, primary_key=True)
    tamanho = models.DecimalField(max_digits=50, decimal_places=2, choices=BOOTS_CHOICES)

    def __str__(self):
        return self.id.nome


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



