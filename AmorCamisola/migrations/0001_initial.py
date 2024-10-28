# Generated by Django 5.1.1 on 2024-10-28 16:35

import django.db.models.deletion
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Following',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('followed', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='followed_id', to=settings.AUTH_USER_MODEL)),
                ('following', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='follower_id', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Moderator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('image', models.ImageField(upload_to='produtos')),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('team', models.CharField(max_length=50, null=True)),
                ('description', models.TextField()),
                ('sold', models.BooleanField(default=False)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Jersey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], max_length=50)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='AmorCamisola.product')),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='AmorCamisola.product')),
            ],
        ),
        migrations.CreateModel(
            name='Boots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.DecimalField(choices=[(36, 36), (36.5, 36.5), (37, 37), (37.5, 37.5), (38, 38), (38.5, 38.5), (39, 39), (39.5, 39.5), (40, 40), (40.5, 40.5), (41, 41), (41.5, 41.5), (42, 42), (42.5, 42.5), (43, 43), (43.5, 43.5), (44, 44), (44.5, 44.5), (45, 45), (45.5, 45.5), (46, 46), (46.5, 46.5), (47, 47)], decimal_places=2, max_digits=50)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='AmorCamisola.product')),
            ],
        ),
        migrations.CreateModel(
            name='Shorts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], max_length=50)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='AmorCamisola.product')),
            ],
        ),
        migrations.CreateModel(
            name='Socks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(choices=[('S', 'S'), ('M', 'M'), ('L', 'L')], max_length=50)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='AmorCamisola.product')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cc', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=50)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True)),
                ('wallet', models.DecimalField(decimal_places=2, default=0, max_digits=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
