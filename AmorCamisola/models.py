import uuid
from django.db import models

# Create your models here.
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    primeiroNome = models.CharField(max_length=50)
    ultimoNome = models.CharField(max_length=50)
    cc = models.CharField(max_length=50)
    wallet = models.DecimalField(max_digits=50, decimal_places=2)
    following = models.ManyToManyField(to="self", related_name="followings", symmetrical=False)

    def __str__(self):
        return self.username


class Moderador(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

class Produto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=50)
    vendedor = models.ManyToOneRel(User, on_delete=models.CASCADE, field_name='user')
    #compra = models.ManyToOneRel(Purchase) isto seria caso tenhamos historico de compras
    preco = models.DecimalField(max_digits=5, decimal_places=2)
    equipa = models.CharField(max_length=50)
    descricao = models.TextField()
    favorited = models.ManyToManyField(User) #não dá para meter isto no user

    def __str__(self):
        return self.nome

class Camisola(models.Model):
    SIZE_CHOICES = ("XS", "S", "M", "L", "XL", "XXL")
    id = models.OneToOneField(Produto, on_delete=models.CASCADE, primary_key=True)
    tamanho = models.CharField(max_length=50, choices=SIZE_CHOICES)

    def __str__(self):
        return self.id.nome

class Calcoes(models.Model):
    SIZE_CHOICES = ("XS", "S", "M", "L", "XL", "XXL")
    id = models.OneToOneField(Produto, on_delete=models.CASCADE, primary_key=True)
    tamanho = models.CharField(max_length=50, choices=SIZE_CHOICES)

    def __str__(self):
        return self.id.nome

class Meias(models.Model):
    id = models.OneToOneField(Produto, on_delete=models.CASCADE, primary_key=True)
    tamanho = models.PositiveIntegerField()

    def __str__(self):
        return self.id.nome

class Chuteiras(models.Model):
    id = models.OneToOneField(Produto, on_delete=models.CASCADE, primary_key=True)
    tamanho = models.PositiveIntegerField()

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



