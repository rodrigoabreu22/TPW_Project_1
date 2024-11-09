from datetime import datetime
from itertools import product, count
from django.http import JsonResponse

from AmorCamisola.forms import *
from AmorCamisola.models import *
from django.contrib.auth.models import Group

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.db.models import Count

from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

# Define the test function for checking if the user is a moderator
def is_moderator(user):
    print("Cucu")
    print(user.groups.filter(name='Moderators').exists())
    return user.groups.filter(name='Moderators').exists()

# Custom decorator for requiring moderator status
def moderator_required(view_func):
    @login_required(login_url='/login/')
    @user_passes_test(is_moderator, login_url='/login/')
    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapped_view

# Example moderator dashboard view
@moderator_required
def moderator_dashboard(request):
    # Get all reports
    all_reports = Report.objects.all()

    # Initialize lists for storing unique reports
    user_reports = []
    product_reports = []

    # Track counts of reports for each user
    seen_users = {}
    for report in all_reports.filter(reporting__isnull=False):
        reporting_id = report.reporting.id
        if reporting_id not in seen_users:
            # Initialize count for new user
            seen_users[reporting_id] = {'report': report, 'count': 1}
        else:
            # Increment count for existing user
            seen_users[reporting_id]['count'] += 1

    # Track counts of reports for each product
    seen_products = {}
    for report in all_reports.filter(product__isnull=False):
        product_id = report.product.id
        if product_id not in seen_products:
            # Initialize count for new product
            seen_products[product_id] = {'report': report, 'count': 1}
        else:
            # Increment count for existing product
            seen_products[product_id]['count'] += 1

    # Convert dictionaries to lists for the context
    user_reports = list(seen_users.values())
    product_reports = list(seen_products.values())

    context = {
        'user_reports': user_reports,
        'product_reports': product_reports,
    }

    return render(request, 'moderator_dashboard.html', context)

@moderator_required
def close_report(request, report_id):
    # Get the report instance
    report = get_object_or_404(Report, id=report_id)
    if report:
        report.delete()
        # Display a success message
        messages.success(request, 'Report has been deleted successfully.')
    else:
        print("Algo de errado não está certo")
    # Redirect to the moderator dashboard or another appropriate page
    return redirect('moderator_dashboard')


@moderator_required
def ban_user(request, user_id):
    # Retrieve the user and their products
    user = get_object_or_404(User, id=user_id)
    user_products = Product.objects.filter(seller=user)

    # Deactivate the user's account
    user.is_active = False
    user.save()

    for product in user_products:
        product.is_active = False
        product.save()

    # Process offers related to the user as a buyer or seller
    related_offers = Offer.objects.filter(
        models.Q(buyer=user.userprofile) | models.Q(product__seller=user)
    )

    for offer in related_offers:
        if offer.product.seller == user:
            # Credit the buyer’s wallet for canceled offers where the user is the seller
            buyer_profile = offer.buyer
            buyer_profile.wallet += offer.value  # Assuming wallet is a field in UserProfile
            buyer_profile.save()

        # Delete the offer after processing
        offer.delete()

    messages.success(request, f"User {user.username} has been banned and associated data processed.")
    return redirect('moderator_dashboard')


@moderator_required
def unban_user(request, user_id):
    # Retrieve the user and their products
    user = get_object_or_404(User, id=user_id)
    user_products = Product.objects.filter(seller=user)

    # Reactivate the user's account
    user.is_active = True
    user.save()

    # Make the user's products accessible again
    for product in user_products:
        product.is_active = True
        product.save()

    messages.success(request, f"User {user.username} has been unbanned and their products are now accessible.")
    return redirect('moderator_dashboard')

@moderator_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, f"Product '{product.name}' has been deleted.")
    return redirect('moderator_dashboard')


# Create your views here.

@login_required
def favorite_list(request):
    favorite_form = FavoriteForm(request.POST or None)
    user_profile = None
    if request.user.is_authenticated:
        favorite_, _ = Favorite.objects.get_or_create(user=request.user)
        products = favorite_.products.all()
        favorites = favorite_.products.values_list('id', flat=True)
        user_profile = UserProfile.objects.get(user=request.user)

        if favorite_form.is_valid():
            product_id = favorite_form.cleaned_data['favorite_product_id']
            product = get_object_or_404(Product, id=product_id)
            print(f"Product ID: {product.id}")  # Debug
            if product in favorite_.products.all():
                favorite_.products.remove(product)
                print(f"Product {product.id} removed from favorites.")  # Debug
            else:
                favorite_.products.add(product)
                print(f"Product {product.id} added to favorites.")  # Debug
            return redirect('favorite_list')
        else:
            print(f"WOMP WOMP WOMP WOMP WOMP WOMP")
    return render(request, 'favorites.html', {
        'favorite_form': favorite_form,
        'favorites_ids': favorites,
        'products': products,
        'profile': user_profile
    })

def home(request):
    print("Test")
    form = ProductQuery(request.GET or None)
    favorite_form = FavoriteForm(request.POST or None)
    products = Product.objects.all()  # Start with all products
    teams=[]
    product_types=[]
    favorites=[]
    user_profile=None
    if form.is_valid():
        name_query = form.cleaned_data['name_query']
        user_query = form.cleaned_data['user_query']
        teams = form.cleaned_data['teams']
        product_types = form.cleaned_data['product_types']
        print("OLA")
        print(product_types)
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
            if 'Camisola' in product_types:
                product_ids += Jersey.objects.values_list('product_id', flat=True)
            if 'Calções' in product_types:
                product_ids += Shorts.objects.values_list('product_id', flat=True)
            if 'Meias' in product_types:
                product_ids += Socks.objects.values_list('product_id', flat=True)
            if 'Chuteiras' in product_types:
                product_ids += Boots.objects.values_list('product_id', flat=True)
            if product_ids:
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


    if request.user.is_authenticated:
        favorite_, _ = Favorite.objects.get_or_create(user=request.user)
        favorites = favorite_.products.values_list('id', flat=True)

        if favorite_form.is_valid():
            product_id = favorite_form.cleaned_data['favorite_product_id']
            product = get_object_or_404(Product, id=product_id)
            print(f"Product ID: {product.id}")  # Debug
            if product in favorite_.products.all():
                favorite_.products.remove(product)
                print(f"Product {product.id} removed from favorites.")  # Debug
            else:
                favorite_.products.add(product)
                print(f"Product {product.id} added to favorites.")  # Debug
            return redirect('home')
        else:
            user_profile = UserProfile.objects.get(user=request.user)

    final_products = []
    for product in products:
        if product.seller.is_active:
            final_products.append(product)

    return render(request, 'home.html', {
        'form': form,
        'favorite_form': favorite_form,
        'products': final_products,
        'selected_teams': teams,
        'selected_types': product_types,
        'favorites_ids': favorites,
        'profile': user_profile
    })



def createAccount(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        print(form.errors)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # Save the user (this automatically hashes the password)
            user = form.save(commit=True)

            # Add the user to the 'Users' group
            group = Group.objects.get(name='Users')
            user.groups.add(group)

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
        form = CreateAccountForm()
    return render(request, 'createAccount.html', {'form': form, 'error': False})

@login_required(login_url='/login/')  # Redirects to login if not authenticated
def myProfile(request):
    user = User.objects.get(id=request.user.id)
    # Get the list of users the current user is following
    following = Following.objects.filter(following=user)
    # Get the list of users who follow the current user
    followers = Following.objects.filter(followed_id=user.id)

    selling = Product.objects.filter(seller_id=request.user.id)
    profile = UserProfile.objects.get(user=request.user)

    tparams = {"user" : user, "following" : following, "followers" : followers, "products" : selling, "profile" : profile  }

    return render(request, 'myProfile.html', tparams)

def viewProfile(request, username):
    profile_user = User.objects.get(username=username)
    print("profile user: ",profile_user)
    # Check if the user is banned
    is_banned = not profile_user.is_active
    print(is_banned)

    favorite_form = FavoriteForm(request.POST or None)

    following = Following.objects.filter(following_id=profile_user.id)
    followers = Following.objects.filter(followed_id=profile_user.id)
    print(followers)
    selling = Product.objects.filter(seller_id=profile_user.id)
    profile = UserProfile.objects.get(user=profile_user)

    if request.user.is_authenticated:
        #favoritos codigo
        favorite_, _ = Favorite.objects.get_or_create(user=request.user)
        favorites = favorite_.products.values_list('id', flat=True)

        if favorite_form.is_valid():
            product_id = favorite_form.cleaned_data['favorite_product_id']
            product = get_object_or_404(Product, id=product_id)
            print(f"Product ID: {product.id}")  # Debug
            if product in favorite_.products.all():
                favorite_.products.remove(product)
                print(f"Product {product.id} removed from favorites.")  # Debug
            else:
                favorite_.products.add(product)
                print(f"Product {product.id} added to favorites.")  # Debug
            return redirect('profile', username=username)



        print("Aconteceu")
        # Report form handling
        if request.method == 'POST' and 'report_user' in request.POST:
            print("Report user")
            report_form = ReportForm(request.POST)

            report_form.instance.sent_by = request.user
            report_form.instance.reporting = profile_user
            if report_form.is_valid():
                print("Valid Report form")
                report = report_form.save(commit=False)
                report.save()
                messages.success(request, 'Usuário reportado com sucesso.')
                return redirect('profile', username=username)
            else:
                print("Form errors:", report_form.errors)
        else:
            report_form = ReportForm()

        user = User.objects.get(id=request.user.id)
        if user == profile_user:
            return myProfile(request)
        follows=False;
        for f in followers:
            print(user.username, " == ", f.following.username)
            if user.username == f.following.username:
                follows = True
                print("follows true")
        tparams = {"is_banned": is_banned,"user": user,'favorite_form': favorite_form,'favorites_ids': favorites, "profile_user": profile_user, "following": following, "followers": followers, "products": selling, "profile": profile, "follows":follows, "offer_count": getOffersCount(request), "report_form": report_form}
    else:
        tparams = {"is_banned": is_banned,"profile_user": profile_user, "following": following, "followers": followers,"products": selling, "profile": profile, "offer_count": getOffersCount(request)}

    return render(request, 'profile.html', tparams)

@login_required(login_url='/login/')  # Redirects to login if not authenticated
def pubProduct(request):
    user_profile = User.objects.get(id=request.user.id)
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
                        return render(request, 'publishProduct.html', {'form': form, 'error': True, "offer_count": getOffersCount(request), "profile": user_profile})

                    if size in [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]:
                        boots = Boots(product=product, size=size)
                        boots.save()

                return redirect('/')
        else:
            return render(request, 'publishProduct.html', {'form': form, 'error': True, "offer_count": getOffersCount(request), "profile": user_profile})
    else:
        form = ProductForm()
    return render(request, 'publishProduct.html', {'form': form, 'error': False, "offer_count" : getOffersCount(request), "profile": user_profile})

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
    # Initialize the search form
    form = SearchUserForm(request.POST or None)
    query = None
    all_users = None
    all_user_profiles = None
    myprofile = None
    if request.user.is_authenticated:
        myprofile = UserProfile.objects.get(user=request.user)

    # Fetch the 10 most popular users based on follower count
    popular_users = (
        User.objects.annotate(num_followers=Count('followers_set'))
        .order_by('-num_followers')[:10]
    )
    # Fetch the UserProfile objects for popular users
    popular_users_profiles = UserProfile.objects.filter(user__in=popular_users)

    # Check if a search query is submitted
    if request.method == 'POST' and form.is_valid():
        query = form.cleaned_data['query']
        # Filter users by username matching the query
        all_users = User.objects.filter(username__icontains=query)
        # Fetch UserProfile objects for the search results
        print(all_users)
        all_user_profiles = UserProfile.objects.filter(user__in=all_users)
        print(all_user_profiles)

    # Render the template with the user data and profiles
    return render(request, 'userList.html', {
        'form': form,
        'popular_users': popular_users,
        'popular_users_profiles': popular_users_profiles,
        'all_users': all_users,
        'all_user_profiles': all_user_profiles,
        'query': query,
        'offer_count' : getOffersCount(request),
        'profile' : myprofile
    })




def detailedProduct(request, id):
    print(request)
    print("OLA")
    print(id)
    product = Product.objects.get(id=id)
    if Jersey.objects.filter(product=product).exists():
        category = "camisola"
        product = Jersey.objects.get(product=product)
    elif Shorts.objects.filter(product=product).exists():
        category = "calções"
        product = Shorts.objects.get(product=product)
    elif Socks.objects.filter(product=product).exists():
        category = "meias"
        product = Socks.objects.get(product=product)
    elif Boots.objects.filter(product=product).exists():
        category = "chuteiras"
        product = Boots.objects.get(product=product)


    user = User.objects.get(id=request.user.id)
    sellerProfile = UserProfile.objects.get(user = product.seller)
    try:
        userProfile = UserProfile.objects.get(user__id=request.user.id)
    except UserProfile.DoesNotExist:
        userProfile = None
    if request.method == 'POST' and 'proposta' in request.POST:
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
            sent_by = userProfile
            offer = Offer(buyer=buyer, product=product, value=value, address=address, payment_method=payment_method, delivery_method=delivery_method, sent_by=sent_by)
            offer.save()
            print("saved")
        redirect('/')
    form = ListingOffer(userProfile, product)

    if request.user.is_authenticated:
        print("Aconteceu")
        # Report form handling
        if request.method == 'POST' and 'report_product' in request.POST:
            print("Report product")
            report_form = ReportForm(request.POST)

            report_form.instance.sent_by = request.user
            report_form.instance.product = product
            if report_form.is_valid():
                print("Valid Report form")
                report = report_form.save(commit=False)
                report.save()
                messages.success(request, 'Produto reportado com sucesso.')
                return redirect('detailedproduct',id=id)
            else:
                print("Form errors:", report_form.errors)
        else:
            report_form = ReportForm()

    tparams = {"product": product, 'form': form, 'profile': userProfile, 'user' : user, 'offer_count' : getOffersCount(request), 'sellerProfile': sellerProfile, 'category': category, "report_form": report_form}
    error = ""
    if product.seller == request.user:
        error = "Próprio produto"
    print(request.user)
    allOffers = Offer.objects.filter(buyer_id=userProfile.id, product=product, offer_status="in_progress")
    print(allOffers)
    if allOffers.__len__() != 0:
        error = "Já apresentou uma oferta por este produto"
    tparams = {"product": product, 'form': form, 'userProfile': userProfile, 'user' : user, 'error': error, 'offer_count' : getOffersCount(request)}
    return render(request, 'productDetailed.html', tparams)

def offers(request, action=None, id=None):
    user = User.objects.get(id=request.user.id)
    userProfile = UserProfile.objects.get(user__id=request.user.id)
    if not action is None:
        if action == 'accept':
            notifySuccess(id)
        elif action == 'reject':
            notifyFailed(id)
        elif action == 'counter':
            if request.method == 'POST':
                form = ListingOffer(userProfile, None, request.POST, request.FILES)
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
                    offer = Offer.objects.get(id=id)
                    offer.payment_method = payment_method
                    offer.delivery_method = delivery_method
                    offer.address = address
                    offer.value = value
                    offer.sent_by = user
                    offer.save()
                    print("saved")
        redirect("/offers")
    form = ListingOffer(userProfile, None)
    madeOffers = Offer.objects.filter(sent_by__user_id=request.user.id)
    activeOffers = madeOffers.filter(offer_status__exact="in_progress")
    receivedOffers = Offer.objects.filter(product__seller_id=request.user.id) | Offer.objects.filter(buyer_id=request.user.id)
    receivedOffersFiltered = receivedOffers.exclude(sent_by__user_id=request.user.id).filter(offer_status__exact='in_progress')
    acceptedOffers = receivedOffers.filter(offer_status__exact='accepted') | madeOffers.filter(offer_status__exact='accepted')
    acceptedNotProcessed = acceptedOffers.exclude(delivered=True, paid=True)
    acceptedAndProcessed = acceptedOffers.filter(delivered=True, paid=True)
    rejectedOffers = receivedOffers.filter(offer_status__exact='rejected') | madeOffers.filter(offer_status__exact='rejected')
    processedOffers = acceptedAndProcessed | rejectedOffers
    tparams = {"profile": userProfile, "user": user, 'offers_received': receivedOffersFiltered, 'offers_made': activeOffers, 'offers_accepted': acceptedNotProcessed, 'offers_rejected': processedOffers, 'form': form, 'offer_count' : getOffersCount(request)}
    return render(request, 'offersTemplate.html', tparams)

def acceptOffer(request, id):
    return offers(request, 'accept', id)

def rejectOffer(request, id):
    return offers(request, 'reject', id)

def counterOffer(request, id):
    return offers(request, 'counter', id)

def retractOffer(request, id):
    offer = Offer.objects.get(id=id)
    offer.delete()
    return redirect("/offers/")

#Funções auxiliares
def valid_purchase(user : UserProfile, offer : Offer):
    return user.wallet < offer.value and not offer.product.sold

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
        receivedOffersFiltered = receivedOffers.exclude(sent_by__user_id=request.user.id).filter(offer_status__exact='in_progress')
        return receivedOffersFiltered.count()
    return 0

def notifySuccess(offer_id):
    offer = Offer.objects.get(id=offer_id)
    offer.offer_status = 'accepted'
    #testing
    #offer.paid = True
    #offer.delivered = True
    #end testing
    offer.save()

def notifyFailed(offer_id):
    offer = Offer.objects.get(id=offer_id)
    offer.offer_status = 'rejected'
    offer.save()

@login_required
def walletLogic(request):
    userinfo = UserProfile.objects.get(user=request.user)
    depositoform = DepositForm()
    levantamentoform = WithdrawalForm()

    return render(request, 'wallet.html', {
        'depositoform': depositoform,
        'levantamentoform': levantamentoform,
        'profile': userinfo,
    })

@login_required
def deposit_money(request):
    userinfo = UserProfile.objects.get(user=request.user)
    depositoform = DepositForm(request.POST or None)

    if request.method == "POST" and depositoform.is_valid():
        deposit_amount = depositoform.cleaned_data['deposit_amount']
        userinfo.wallet += deposit_amount
        userinfo.save()
        messages.success(request, "Depósito foi bem-sucedido!")
        return redirect('wallet')  # Redirect back to main wallet page

    # If form is invalid, render the page with errors
    levantamentoform = WithdrawalForm()  # Provide empty form to avoid errors
    return render(request, 'wallet.html', {
        'depositoform': depositoform,
        'levantamentoform': levantamentoform,
        'profile': userinfo,
    })

@login_required
def withdraw_money(request):
    userinfo = UserProfile.objects.get(user=request.user)
    levantamentoform = WithdrawalForm(request.POST or None)

    if request.method == "POST" and levantamentoform.is_valid():
        withdrawal_amount = levantamentoform.cleaned_data['withdrawal_amount']
        if withdrawal_amount > userinfo.wallet:
            messages.error(request, "Erro: O valor solicitado excede o saldo da carteira.")
        else:
            userinfo.wallet -= withdrawal_amount
            userinfo.save()
            messages.success(request, "Levantamento foi bem-sucedido!")
        return redirect('wallet')  # Redirect back to main wallet page

    # If form is invalid, render the page with errors
    depositoform = DepositForm()  # Provide empty form to avoid errors
    return render(request, 'wallet.html', {
        'depositoform': depositoform,
        'levantamentoform': levantamentoform,
        'profile': userinfo,
    })

@login_required
def account(request):
    image_form = UploadProfilePicture(request.POST)
    user = request.user
    account = UserProfile.objects.get(user=user)

    return render(request, 'account.html', {'user':user, 'account': account})

@login_required
def accountSettings(request):
    if request.method == 'GET':
        user = request.user
        account = UserProfile.objects.get(user=user)
        image_form = UploadProfilePicture()
        user_form = UpdateUser(initial={'email': user.email, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name})
        profile_form = UpdateProfile(initial={'address':account.address, 'phone':account.phone})
        password_form = UpdatePassword()
        return render(request, 'account.html', {'user': user, 'profile':account,'image_form': image_form, 'user_form': user_form,
                                                         'profile_form': profile_form, 'password_form': password_form})
    elif request.method == 'POST':
        if 'image' in request.FILES:
            user=request.user
            account = UserProfile.objects.get(user=user)
            image_form=UploadProfilePicture(request.POST, request.FILES)
            if image_form.is_valid():
                file = request.FILES['image']

                if file:
                    account.image = file
                    account.update_image(file)
                    account.save()
                    return redirect('/myprofile/settings')
                else:
                    image_form = UploadProfilePicture()
                    print(image_form.errors)
                    return render(request, 'account.html', {'user': user, 'profile':account, 'image_form': image_form})

        elif  'profile_change' in request.POST:
            # get the form info
            user=request.user
            user_profile = UserProfile.objects.get(user=user)
            user_form = UpdateUser(request.POST)
            profile_form = UpdateProfile(request.POST)
            if profile_form.is_valid() and user_form.is_valid():
                if user.username != user_form.cleaned_data['username']:
                    user.username = user_form.cleaned_data['username']
                if user.email != user_form.cleaned_data['email']:
                    user.email = user_form.cleaned_data['email']
                if user.first_name != user_form.cleaned_data['first_name']:
                    user.first_name = user_form.cleaned_data['first_name']
                if user.last_name != user_form.cleaned_data['last_name']:
                    user.last_name = user_form.cleaned_data['last_name']
                user.save()
                if user_profile.phone != profile_form.cleaned_data['phone']:
                    user_profile.phone = profile_form.cleaned_data['phone']
                if user_profile.address != profile_form.cleaned_data['address']:
                    user_profile.address = profile_form.cleaned_data['address']
                user_profile.save()

                return redirect('/myprofile/settings')

        elif 'password_change' in request.POST:
            user = request.user
            account = UserProfile.objects.get(user=user)
            password_form = UpdatePassword(request.POST)
            image_form = UploadProfilePicture()
            user_form = UpdateUser(initial={'email': user.email, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name})
            profile_form = UpdateProfile(initial={'address': account.address, 'phone': account.phone})
            if password_form.is_valid():
                if password_form.cleaned_data['new'] == password_form.cleaned_data['confirm']:
                    request.user.set_password(password_form.cleaned_data['new'])
                    user.save()
                    print('Password changed successfully!')
                    return render(request, 'account.html', {'user': user, 'profile':account, 'password_form': password_form,
                                                                     'image_form': image_form,
                                                                     'profile_form': profile_form,
                                                                     'user_form': user_form,
                                                                     'success': 'Password changed successfully!'})
                else:
                    print('Passwords do not match!')
                    return render(request, 'account.html', {'user': user, 'profile':account, 'password_form': password_form,
                                                                     'image_form': image_form,
                                                                     'profile_form': profile_form,
                                                                     'user_form': user_form,
                                                                     'error': 'Passwords do not match!'})

            else:
                return render(request, 'account.html', {'user': user, 'profile':account, 'password_form': password_form,
                                                                 'image_form': image_form,
                                                                 'profile_form': profile_form,
                                                                 'user_form': user_form,
                                                                 'error': 'Invalid form!'})


