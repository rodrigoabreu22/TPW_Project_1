from datetime import datetime
from AmorCamisola.forms import *
from AmorCamisola.models import *

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect

# Create your views here.

def home(request):
    tparams = {
        'title': 'Home Page',
        'year': datetime.now().year,
    }
    return render(request, 'index.html', tparams)



def createAccount(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        print(form.errors)

        if form.is_valid():

            if User.objects.filter(username=form.cleaned_data['username']):
                return render(request, 'createAccount.html', {'form': form, 'error': True})
            else:
                form.save()
                name = form.cleaned_data['name']
                #lastname = name
                email = form.cleaned_data.get('email')
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                #cc = form.cleaned_data.get('cc')
                #phone = form.cleaned_data.get('phone')

                #user = User(firstname=firstname, lastname=lastname, username=username, email=email, cc=cc, phone=phone, password=make_password(password))
                #user.set_password(password)  # This securely sets the password
                #user.save()

                # Authenticate the user and log them in
                user = authenticate(username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect('/')
                else:
                    # In case authentication fails, return an error message
                    return render(request, 'createAccount.html', {'form': form, 'error': True})
        else:
            # If the form is not valid, re-render with error messages
            return render(request, 'createAccount.html', {'form': form, 'error': True})
    else:
        form = CreateAccountForm()
    return render(request, 'createAccount.html', {'form': form, 'error': False})

def viewProfile(request, user_id=0):
    user = User.objects.filter(id=user_id)
    following = Following.objects.filter(following_id=user_id)
    selling = Product.objects.filter(seller_id=user_id)

    tparams = {"user" : user, "following" : following, "selling" : selling}

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

                seller = request.user.username

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