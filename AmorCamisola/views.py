from datetime import datetime
from itertools import product, count

from AmorCamisola.forms import *
from AmorCamisola.models import *

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.db.models import Count


# Create your views here.

def home(request):
    form = ProductQuery(request.GET or None)
    products = Product.objects.all()  # Start with all products
    teams=[]
    product_types=[]

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
            if not product_ids:
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
            products = products.order_by('seller__username')
        elif sort_by == 'seller_desc':
            products = products.order_by('-seller__username')

    return render(request, 'home.html', {'form': form, 'products': products, 'selected_teams': teams, 'selected_types':product_types, "offer_count": getOffersCount(request)})



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
                return render(request, 'createAccount.html', {'form': form, 'error': 'Authentication failed', "offer_count": getOffersCount(request)})

        else:
            return render(request, 'createAccount.html', {'form': form, 'error': 'Form is not valid', "offer_count": getOffersCount(request)})

    else:
        form = CreateAccountForm()  # GET request, instantiate a blank form
    return render(request, 'createAccount.html', {'form': form, 'error': False, "offer_count": getOffersCount(request)})

@login_required(login_url='/login/')  # Redirects to login if not authenticated
def myProfile(request):
    user = User.objects.get(id=request.user.id)
    # Get the list of users the current user is following
    following = Following.objects.filter(following=user)

    # Get the list of users who follow the current user
    followers = Following.objects.filter(followed_id=user.id)

    selling = Product.objects.filter(seller_id=request.user.id)
    profile = UserProfile.objects.get(user=request.user)

    # Check if the profile user is followed by the logged-in user
    follows = Following.objects.filter(following=request.user, followed=user).exists()
    products = Product.objects.filter(seller_id=request.user.id)

    tparams = {"user" : user, "following" : following, "followers" : followers, "selling" : selling, "profile" : profile, "products": products, "offer_count": getOffersCount(request)}

    return render(request, 'myProfile.html', tparams)

def viewProfile(request, username):
    profile_user = User.objects.get(username=username)
    print("profile user: ",profile_user)

    following = Following.objects.filter(following_id=profile_user.id)
    followers = Following.objects.filter(followed_id=profile_user.id)
    print(followers)
    selling = Product.objects.filter(seller_id=profile_user.id)
    profile = UserProfile.objects.get(user=profile_user)

    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        if user == profile_user:
            return myProfile(request)
        follows=False;
        for f in followers:
            print(user.username, " == ", f.following.username)
            if user.username == f.following.username:
                follows = True
                print("follows true")
        tparams = {"user": user, "profile_user": profile_user, "following": following, "followers": followers,
                       "selling": selling, "profile": profile, "follows":follows, "offer_count": getOffersCount(request)}
    else:
        tparams = {"profile_user": profile_user, "following": following, "followers": followers,"selling": selling, "profile": profile, "offer_count": getOffersCount(request)}

    return render(request, 'profile.html', tparams)

@login_required(login_url='/login/')  # Redirects to login if not authenticated
def pubProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        print(form.errors)
        if form.is_valid():
            if request.user.is_authenticated:
                name = form.cleaned_data['name']
                description = form.cleaned_data['description']
                price = form.cleaned_data['price']
                team = form.cleaned_data['team']
                category = form.cleaned_data['category']
                size = form.cleaned_data['size']
                image = form.cleaned_data['image']

                seller = request.user

                product = Product(name=name, description=description, price=price, team=team, seller=seller, image=image)
                product.save()

                if category == '1':  # Camisola
                    if size in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
                        camisola = Jersey(product=product, size=size)
                        camisola.save()
                elif category == '2':  # Calções
                    if size in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
                        shorts = Shorts(product=product, size=size)
                        shorts.save()
                elif category == '3':  # Meias
                    if size in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
                        socks = Socks(product=product, size=size)
                        socks.save()
                elif category == '4':  # Chuteira
                    try:
                        size = int(size)
                    except ValueError:
                        return render(request, 'publishProduct.html', {'form': form, 'error': True})

                    if size in [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]:
                        boots = Boots(product=product, size=size)
                        boots.save()

                return redirect('/')
        else:
            return render(request, 'publishProduct.html', {'form': form, 'error': True, "offer_count": getOffersCount(request)})
    else:
        form = ProductForm()
    return render(request, 'publishProduct.html', {'form': form, 'error': False, "offer_count" : getOffersCount(request)})

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if not Following.objects.filter(following=request.user, followed=user_to_follow).exists():
        Following.objects.create(following=request.user, followed=user_to_follow)
    return redirect('profile', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    Following.objects.filter(following=request.user, followed=user_to_unfollow).delete()
    return redirect('profile', username=username)

def userlist(request):
    # Inicializar o formulário de pesquisa
    form = SearchUserForm(request.POST or None)
    query = None
    all_users = None

    # Se não houver busca, mostrar os 10 usuários mais populares
    popular_users = (
        User.objects.annotate(num_followers=Count('followers_set'))
        .order_by('-num_followers')[:10]
    )

    # Verificar se uma busca foi realizada
    if request.method == 'POST' and form.is_valid():
        query = form.cleaned_data['query']
        # Filtrar os usuários pelo nome
        all_users = User.objects.filter(username__icontains=query)

    # Renderizar o template com os resultados
    return render(request, 'userList.html', {
        'form': form,
        'popular_users': popular_users,
        'all_users': all_users,
        'query': query,
        'offer_count' : getOffersCount(request)
    })



def detailedProduct(request, id):
    print(request)
    product = Product.objects.get(id=id)
    user = User.objects.get(id=request.user.id)
    try:
        userProfile = UserProfile.objects.get(user__id=request.user.id)
    except UserProfile.DoesNotExist:
        userProfile = None
    if request.method == 'POST':
        form = ListingOffer(userProfile, product, request.POST, request.FILES)
        print(form.errors)
        print(form.cleaned_data['address_choice'])
        print(form.cleaned_data['value'])
        print(form.cleaned_data['delivery_method'])
        print(form.cleaned_data['payment_method'])
        print(form.cleaned_data['custom_address'])
        if form.is_valid():
            print("valid")
            payment_method = form.cleaned_data['payment_method']
            delivery_method = form.cleaned_data['delivery_method']
            address = form.cleaned_data['custom_address']
            value = form.cleaned_data['value']
            buyer = userProfile
            offer = Offer(buyer=buyer, product=product, value=value, address=address, payment_method=payment_method, delivery_method=delivery_method)
            offer.save()
            print("saved")
            redirect('/')
    form = ListingOffer(userProfile, product)
    tparams = {"product": product, 'form': form, 'userProfile': userProfile, 'user' : user, 'offer_count' : getOffersCount(request)}
    return render(request, 'productDetailed.html', tparams)

def offers(request, action=None, id=None):
    user = User.objects.get(id=request.user.id)
    userProfile = UserProfile.objects.get(user__id=request.user.id)
    if not action is None:
        if action == 'accept':
            notifySuccess(id)
        elif action == 'reject':
            notifyFailed(id)
    madeOffers = Offer.objects.filter(sent_by__user_id=request.user.id)
    receivedOffers = Offer.objects.filter(product__seller_id=request.user.id) | Offer.objects.filter(buyer_id=request.user.id)
    receivedOffersFiltered = receivedOffers.exclude(sent_by__user_id=request.user.id)
    tparams = {"userProfile": userProfile, "user": user, 'offers_received': receivedOffersFiltered, 'offers_made': madeOffers, 'offer_count' : getOffersCount(request)}
    return render(request, 'offersTemplate.html', tparams)

def acceptOffer(request, id):
    return offers(request, 'accept', id)

def rejectOffer(request, id):
    return offers(request, 'reject', id)

def notifySuccess(offer_id):
    print("success!")

def notifyFailed(offer_id):
    print("fail!")

#Funções auxiliares
def valid_purchase(user : UserProfile, product : Product):
    return user.wallet < product.price and not product.sold

def perform_sale(buyer : UserProfile, seller : UserProfile, product : Product):
    if valid_purchase(buyer, product):
        buyer.wallet -= product.price
        seller.wallet += product.price
        buyer.save()
        seller.save()
        return True
    return False


def getOffersCount(request):
    if request.user.is_authenticated:
        receivedOffers = Offer.objects.filter(product__seller_id=request.user.id) | Offer.objects.filter(buyer_id=request.user.id)
        receivedOffersFiltered = receivedOffers.exclude(sent_by__user_id=request.user.id)
        return receivedOffersFiltered.count()
    return 0