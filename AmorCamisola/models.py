import uuid
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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

ReportOptions = (
    ("Scam", "Scam"),
    ("Impersonating", "Impersonating"),
    ("Toxic", "Toxic"),
    ("Other", "Other")
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



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=50)
    phone = PhoneNumberField(unique=True, null=False, blank=False)
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

class ReportOptions(models.TextChoices):
    INAPPROPRIATE = 'IN', 'Inappropriate Content'
    FRAUD = 'FR', 'Fraud'
    IMPERSONATE = 'IM', 'Impersonate'
    OTHER = 'OT', 'Other'

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
        # Ensure either 'reporting' or 'product' is set, but not both
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
    size = models.CharField(max_length=50, choices=SOCKS_CHOICES)

    def __str__(self):
        return self.product.__str__()


class Boots(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    size = models.DecimalField(max_digits=50, decimal_places=2, choices=BOOTS_CHOICES)

    def __str__(self):
        return self.product.__str__()


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



