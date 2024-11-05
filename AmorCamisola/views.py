from datetime import datetime
from AmorCamisola.forms import *
from AmorCamisola.models import *

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect

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
        print(form.errors)  # Debugging: See form errors if the form is not valid

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # Save the user (this automatically hashes the password)
            user = form.save(commit=True)

            # Authenticate and log the user in
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('/')  # Redirect to home or another page
            else:
                return render(request, 'createAccount.html', {'form': form, 'error': 'Authentication failed'})

        else:
            return render(request, 'createAccount.html', {'form': form, 'error': 'Form is not valid'})

    else:
        form = CreateAccountForm()  # GET request, instantiate a blank form
    return render(request, 'createAccount.html', {'form': form, 'error': False})

def viewProfile(request):
    user = User.objects.get(id=request.user.id)
    following = Following.objects.filter(following_id=request.user.id)
    selling = Product.objects.filter(seller_id=request.user.id)
    profile = UserProfile.objects.get(user=request.user)

    tparams = {"user" : user, "followList" : following, "selling" : selling, "profile" : profile}

    return render(request, 'profilePage.html', tparams)

def pubProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        print(form.errors)

        if form.is_valid():
            if request.user.is_authenticated:
                name = form.cleaned_data['name']
                description = form.cleaned_data['description']
                price = form.cleaned_data['price']
                team = form.cleaned_data['team']
                category = form.cleaned_data['category']
                size = form.cleaned_data['size']

                seller = request.user

                product = Product(name=name, description=description, price=price, team=team, seller=seller)
                product.save()

                if category == "Camisola":
                    if size in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
                        camisola = Jersey(product=product.id, size=size)
                        camisola.save()
                elif category == "Shorts":
                    if size in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
                        shorts = Shorts(product=product.id, size=size)
                        shorts.save()
                elif category == "Socks":
                    if size in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
                        socks = Socks(product=product.id, size=size)
                        socks.save()
                elif category == "Boots":
                    try:
                        size = int(size)
                    except ValueError:
                        return render(request, 'publishProduct.html', {'form': form, 'error': True})

                    if size in [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]:
                        socks = Socks(product=product.id, size=size)
                        socks.save()

                return redirect('/')
        else:
            return render(request, 'publishProduct.html', {'form': form, 'error': True})
    else:
        form = ProductForm()
    return render(request, 'publishProduct.html', {'form': form, 'error': False})