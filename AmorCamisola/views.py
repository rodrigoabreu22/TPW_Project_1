from datetime import datetime
from AmorCamisola.forms import *
from AmorCamisola.models import *

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect

from django.contrib.auth.hashers import make_password

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.

def home(request):
    form = ProductQuery(request.GET or None)
    products = Product.objects.all()  # Start with all products

    if form.is_valid():
        name_query = form.cleaned_data['name_query']
        user_query = form.cleaned_data['user_query']
        teams = form.cleaned_data['teams']
        product_types = form.cleaned_data['product_types']
        min_price = form.cleaned_data['min_price']
        max_price = form.cleaned_data['max_price']
        sort_by = form.cleaned_data['sort_by']

        # Filtering logic
        if name_query:
            products = products.filter(name__icontains=name_query)
        if user_query:
            products = products.filter(seller__username__icontains=user_query)
        if teams:
            products = products.filter(team__in=teams)
        if product_types:
            product_ids = []
            if 'Jersey' in product_types:
                product_ids += Jersey.objects.values_list('product_id', flat=True)
            if 'Shorts' in product_types:
                product_ids += Shorts.objects.values_list('product_id', flat=True)
            if 'Socks' in product_types:
                product_ids += Socks.objects.values_list('product_id', flat=True)
            if 'Boots' in product_types:
                product_ids += Boots.objects.values_list('product_id', flat=True)

            products = products.filter(id__in=product_ids)
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

        # Sorting logic
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
        elif sort_by == 'seller_asc':
            products = products.order_by('seller')
        elif sort_by == 'seller_desc':
            products = products.order_by('-seller')

    return render(request, 'home.html', {'form': form, 'products': products})



def createAccount(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        print(form.errors)

        if form.is_valid():

            if User.objects.filter(username=form.cleaned_data['username']):
                return render(request, 'createAccount.html', {'form': form, 'error': True})
            else:
                firstname = form.cleaned_data['firstname']
                lastname = form.cleaned_data['lastname']
                email = form.cleaned_data.get('email')
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                cc = form.cleaned_data.get('cc')

                user = User(firstname=firstname, lastname=lastname, username=username, email=email, cc=cc, password=make_password(password))
                user.save()

                user = authenticate(username=username, password=password)
                #auth_login(request, user)

                return redirect('/')
        else:
            return render(request, 'createAccount.html', {'form': form, 'error': True})
    else:
        form = CreateAccountForm()
    return render(request, 'createAccount.html', {'form': form, 'error': False})

def viewProfile(request, user_id=0):
    user = User.objects.get(id=user_id)
    #user = User.objects.all()[0]
    following = Following.objects.filter(following_id=user_id)
    selling = Product.objects.filter(seller_id=user_id)

    tparams = {"user" : user, "followList" : following, "selling" : selling}

    return render(request, 'profilePage.html', tparams)