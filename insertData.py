import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TPW_Project_1.settings')
django.setup()

from django.contrib.auth.models import User, Group
from AmorCamisola.models import UserProfile, Product, Jersey, Shorts, Socks, Boots, Favorite, Following, Report, Offer


def create_users():
    manel = User.objects.create_user(first_name='Manel', last_name='Lopes', email='manel@gmail.com', username='manel', password='password123')
    martim = User.objects.create_user(first_name='Martim', last_name='Antunes', email='martim@gmail.com', username='martim', password='password123')
    tony = User.objects.create_user(first_name='Tony', last_name='Carreira', email='tony@gmail.com', username='tony', password='password123')

    users_group, created = Group.objects.get_or_create(name='Users')
    manel.groups.add(users_group)
    martim.groups.add(users_group)
    tony.groups.add(users_group)

    # Set moderator as a moderator
    moderator_group, created = Group.objects.get_or_create(name='Moderators')
    manel.groups.add(moderator_group)


    UserProfile.objects.create(user=manel, address="Rua do Manel", phone="987654322", image='users/manel.jpeg')
    UserProfile.objects.create(user=martim, address="Rua do Martim", phone="987654323", image='users/martim.jpeg')
    UserProfile.objects.create(user=tony, address="Rua do Tony", phone="987654324", image='users/tony.jpeg')


    return manel, martim, tony

# Create products
def create_products(users):
    product_types = {
        'Jersey': Jersey,
        'Shorts': Shorts,
        'Socks': Socks,
        'Boots': Boots
    }

    products = []
    product_data = [
        ('Jersey','Camisola do Benfica 2022/23', users[2], 50, 'produtos/camisola_benfica.jpg', 'Camisola em bom estado, raramente usada. Decidi vender porque comprei uma nova.', 'Benfica' ),
        ('Shorts', 'Calções do Benfica 2022/23', users[2], 30, 'produtos/calcoes_benfica.jpg', 'Calções em bom estado, raramente usada. Decidi vender porque comprei uns novos.', 'Benfica' ),
        ('Socks', 'Meias de Futebol Pretas', users[2], 5, 'produtos/meias3.jpg', 'Meias em bom estado, raramente usada. Decidi vender porque já não pratico a modalidade.', 'Nenhum'),
        ('Boots', 'Chuteiras Adidas Copa', users[2], 70, 'produtos/adidas_copa.jpg', 'Chuteiras em bom estado, raramente usada. Decidi vender porque já não pratico a modalidade.', 'Nenhum'),
        ('Jersey', 'Camisola Real Madrid 2022/23', users[0], 60, 'produtos/camisola_real.jpg', 'Camisola em bom estado, raramente usada. Decidi vender porque comprei uma nova.', 'Real Madrid' ),
        ('Shorts', 'Calções do Real Madrid 2022/23', users[0], 20, 'produtos/calcoes_real.jpg', 'Calções em bom estado, raramente usada. Decidi vender porque comprei uns novos.', 'Real Madrid' ),
        ('Socks', 'Meias de Futebol Brancas', users[0], 5, 'produtos/meias2.jpg', 'Meias em bom estado, raramente usada. Decidi vender porque já não pratico a modalidade.', 'Nenhum'),
        ('Boots', 'Chuteiras Nike Mercurial', users[0], 80, 'produtos/nike_mercurial.jpg', 'Chuteiras em bom estado, raramente usadas. Decidi vender porque já não pratico a modalidade.', 'Nenhum'),
        ('Jersey', 'Camisola do Sporting 2022/23', users[1], 50, 'produtos/camisola_sporting.jpg', 'Camisola em bom estado, raramente usada. Decidi vender porque mudei de clube para um clube melhor (Benfica).', 'Sporting'),
        ('Shorts', 'Calções do Sporting 2022/23', users[1], 30, 'produtos/calcoes_sporting.jpg','Calções em bom estado, raramente usada. Decidi vender porque mudei de clube para um clube melhor (Benfica).', 'Sporting'),
        ('Socks', 'Meias de Futebol Azuis', users[1], 5, 'produtos/meias3.jpg','Meias em bom estado, raramente usada. Decidi vender porque já não pratico a modalidade.', 'Nenhum'),
        ('Boots', 'Chuteiras Adidas Predator', users[1], 60, 'produtos/adidas_predator.jpg','Chuteiras em bom estado, raramente usadas. Decidi vender porque já não pratico a modalidade.', 'Nenhum'),
    ]

    for product_type, name, seller, price, image, description, team in product_data:
        product = Product.objects.create(
            name=name,
            seller=seller,
            price=price,
            team=team,
            description=description,
            image=image
        )
        if product_type == 'Boots':
            size = 42
        else:
            size = "M"
        product_instance = product_types[product_type].objects.create(product=product, size=size)
        products.append(product)

    return products


# Create favorites
def create_favorites(user, products):
    favorite, created = Favorite.objects.get_or_create(user=user)
    favorite.products.set(products[:3])  # Add first 3 products to favorites


# Create following relationships
def create_following(manel, martim, tony):
    Following.objects.create(following=martim, followed=manel)
    Following.objects.create(following=tony, followed=manel)
    Following.objects.create(following=manel, followed=tony)


# Populate the database
def populate_database():
    manel, martim, tony = create_users()
    products = create_products([manel, martim, tony])
    create_favorites(manel, products)
    create_following(manel, martim, tony)


populate_database()
print("Database populated successfully.")