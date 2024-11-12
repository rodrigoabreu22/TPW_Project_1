from AmorCamisola.forms import *
from AmorCamisola.models import *
from django.contrib.auth.models import Group

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Count, Case, When

from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from django.contrib.auth import views as auth_views
from django.urls import reverse

def verifyIfAdmin(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return True
    return False

# Define the test function for checking if the user is a moderator
def is_moderator(user):
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
    if verifyIfAdmin(request):
        return redirect("/admin")
    all_reports = Report.objects.all()

    # Track counts of reports for each user
    seen_users = {}
    for report in all_reports.filter(reporting__isnull=False):
        reporting_id = report.reporting.id
        if reporting_id not in seen_users:
            seen_users[reporting_id] = {'report': report, 'count': 1}
        else:
            seen_users[reporting_id]['count'] += 1

    # Track counts of reports for each product
    seen_products = {}
    for report in all_reports.filter(product__isnull=False):
        product_id = report.product.id
        if product_id not in seen_products:
            seen_products[product_id] = {'report': report, 'count': 1}
        else:
            seen_products[product_id]['count'] += 1

    user_reports = list(seen_users.values())
    product_reports = list(seen_products.values())

    logged = UserProfile.objects.get(user=request.user)

    context = {
        'user_reports': user_reports,
        'product_reports': product_reports,
        'offer_count': getOffersCount(request),
        'profile': logged
    }

    return render(request, 'moderator_dashboard.html', context)

@moderator_required
def user_mod_view(request,username):
    if verifyIfAdmin(request):
        return redirect("/admin")
    profile_user = User.objects.get(username=username)
    print("profile user: ", profile_user)

    following = Following.objects.filter(following_id=profile_user.id)
    followers = Following.objects.filter(followed_id=profile_user.id)
    print(followers)
    selling = Product.objects.filter(seller_id=profile_user.id)

    reports = Report.objects.filter(reporting=profile_user)

    logged= UserProfile.objects.get(user=request.user)

    tparams = {"profile_user": profile_user, "following": following, "followers": followers, "products": selling,
               "offer_count": getOffersCount(request), "reports": reports,
        'profile': logged}

    return render(request, 'profile_moderatorview.html', tparams)



@moderator_required
def product_mod_view(request, product_id):
    if verifyIfAdmin(request):
        return redirect("/admin")
    product = Product.objects.get(id=product_id)
    if Jersey.objects.filter(product=product).exists():
        category = "camisola"
        p = Jersey.objects.get(product=product)
    elif Shorts.objects.filter(product=product).exists():
        category = "calções"
        p = Shorts.objects.get(product=product)
    elif Socks.objects.filter(product=product).exists():
        category = "meias"
        p = Socks.objects.get(product=product)
    elif Boots.objects.filter(product=product).exists():
        category = "chuteiras"
        p = Boots.objects.get(product=product)

    user = User.objects.get(id=request.user.id)
    sellerProfile = UserProfile.objects.get(user=product.seller)
    try:
        userProfile = UserProfile.objects.get(user__id=request.user.id)
    except UserProfile.DoesNotExist:
        userProfile = None

    reports = Report.objects.filter(product=product)

    tparams = {"product": p,"reports":reports, 'profile': userProfile, 'user': user, 'offer_count': getOffersCount(request),
               'sellerProfile': sellerProfile, 'category': category}
    return render(request, 'product_moderatorview.html', tparams)

@moderator_required
def close_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if report:
        report.delete()
        messages.success(request, 'Report has been deleted successfully.')
    else:
        print("Algo de errado não está certo")
    return redirect('moderator_dashboard')


@moderator_required
def ban_user(request, user_id):
    print("Banning")
    user = get_object_or_404(User, id=user_id)
    user_products = Product.objects.filter(seller=user)

    user.is_active = False
    user.save()

    for product in user_products:
        product.is_active = False
        product.save()

    related_offers = Offer.objects.filter(
        models.Q(buyer=user.userprofile) | models.Q(product__seller=user)
    )


    for offer in related_offers:
        print(offer)
        offer_status_conditions = offer.paid and not offer.delivered

        offer_status_conditions2 = offer.offer_status in ["accepted","rejected"] and not offer.paid and not offer.delivered

        offer_status_conditions3 = offer.offer_status in ["in_progress"]

        print(offer.product)

        buyer_profile = offer.buyer
        seller_profile = UserProfile.objects.get(user=offer.product.seller)

        if (offer.product.seller == user and (offer_status_conditions or offer_status_conditions2)) or \
                (offer.buyer == user and (offer_status_conditions or offer_status_conditions2)):
            print("Condition 1 or 2 met: Transferring money from seller to buyer and deleting offer")

            buyer_profile.wallet += offer.value
            buyer_profile.save()
            seller_profile.wallet -= offer.value
            seller_profile.save()

            offer.delete()

        elif offer_status_conditions3:
            print("Condition 3 met: Adding money to buyer and deleting offer")

            buyer_profile.wallet += offer.value
            buyer_profile.save()

            offer.delete()

    messages.success(request, f"User {user.username} has been banned and associated data processed.")
    return redirect('moderator_dashboard')


@moderator_required
def unban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_products = Product.objects.filter(seller=user)

    user.is_active = True
    user.save()

    for product in user_products:
        product.is_active = True
        product.save()

    messages.success(request, f"User {user.username} has been unbanned and their products are now accessible.")
    return redirect('moderator_dashboard')

@moderator_required
def delete_product(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    related_offers = Offer.objects.filter(
        models.Q(product=product)
    )

    for offer in related_offers:
        print(offer)
        offer_status_conditions = offer.paid and not offer.delivered

        offer_status_conditions2 = offer.offer_status in ["accepted",
                                                          "rejected"] and not offer.paid and not offer.delivered

        offer_status_conditions3 = offer.offer_status in ["in_progress"]

        print(offer.product)

        if offer_status_conditions or offer_status_conditions2:
            print("Condition 1 or 2 met: Transferring money from seller to buyer and deleting offer")

            buyer = offer.buyer
            buyer.wallet += offer.value
            buyer.save()
            seller = offer.product.seller
            seller.wallet -= offer.value
            seller.save()

            offer.delete()

        elif offer_status_conditions3:
            print("Condition 3 met: Adding money to buyer and deleting offer")

            buyer = offer.buyer
            buyer.wallet += offer.value
            buyer.save()

            offer.delete()
    product.delete()
    messages.success(request, f"Product '{product.name}' has been deleted.")
    return redirect('moderator_dashboard')

def delete_product_user(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    related_offers = Offer.objects.filter(
        models.Q(product=product)
    )

    for offer in related_offers:
        print(offer)
        offer_status_conditions = offer.paid and not offer.delivered

        offer_status_conditions2 = offer.offer_status in ["accepted",
                                                          "rejected"] and not offer.paid and not offer.delivered

        offer_status_conditions3 = offer.offer_status in ["in_progress"]

        print(offer.product)

        if offer_status_conditions or offer_status_conditions2:
            print("Condition 1 or 2 met: Transferring money from seller to buyer and deleting offer")

            buyer = offer.buyer
            buyer.wallet += offer.value
            buyer.save()
            seller = offer.product.seller
            seller.wallet -= offer.value
            seller.save()

            offer.delete()

        elif offer_status_conditions3:
            print("Condition 3 met: Adding money to buyer and deleting offer")

            buyer = offer.buyer
            buyer.wallet += offer.value
            buyer.save()

            offer.delete()

    product.delete()
    messages.success(request, f"Product '{product.name}' has been deleted.")
    return redirect('myprofile')


@login_required
def favorite_list(request):
    if verifyIfAdmin(request):
        return redirect("/admin")
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
        'profile': user_profile,
        'offer_count': getOffersCount(request),
    })


class CustomLoginView(auth_views.LoginView):
    template_name = "login.html"

    def form_invalid(self, form):
        username = form.data.get('username')
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                messages.error(self.request, "This account has been banned.")
                return redirect(reverse('login') + '?banned=true')
        except User.DoesNotExist:
            pass

        return super().form_invalid(form)


SIZE_ORDER = {'XS': 0, 'S': 1, 'M': 2, 'L': 3, 'XL': 4}

def get_size_order(size):
    return SIZE_ORDER.get(size, -1)

def home(request):
    print("Test")
    if verifyIfAdmin(request):
        return redirect("/admin")
    form = ProductQuery(request.GET or None)
    favorite_form = FavoriteForm(request.POST or None)
    products = Product.objects.all()
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

    products = products.filter(seller__is_active=True).exclude(sold=True)

    return render(request, 'home.html', {
        'form': form,
        'favorite_form': favorite_form,
        'products': products,
        'selected_teams': teams,
        'selected_types': product_types,
        'favorites_ids': favorites,
        'profile': user_profile,
        'user': request.user,
        'offer_count' : getOffersCount(request)
    })



def createAccount(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = form.save(commit=True)

            group = Group.objects.get(name='Users')
            user.groups.add(group)

            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('/')
            else:
                return render(request, 'createAccount.html', {'form': form, 'error': 'Authentication failed', "offer_count": getOffersCount(request)})

        else:
            return render(request, 'createAccount.html', {'form': form, 'error': 'Form is not valid', "offer_count": getOffersCount(request)})

    else:
        form = CreateAccountForm()
    return render(request, 'createAccount.html', {'form': form, 'error': False, 'offer_count' : getOffersCount(request),})

@login_required(login_url='/login/')
def myProfile(request):
    if verifyIfAdmin(request):
        return redirect("/admin")
    user = User.objects.get(id=request.user.id)
    following = Following.objects.filter(following=user)
    followers = Following.objects.filter(followed_id=user.id)

    selling = Product.objects.filter(seller_id=request.user.id).exclude(sold=True)
    profile = UserProfile.objects.get(user=request.user)

    tparams = {"user" : user, "following" : following, "followers" : followers, "products" : selling, "profile" : profile, 'offer_count' : getOffersCount(request)  }

    return render(request, 'myProfile.html', tparams)

def viewProfile(request, username):
    if verifyIfAdmin(request):
        return redirect("/admin")
    profile_user = User.objects.get(username=username)
    is_banned = not profile_user.is_active
    print(is_banned)

    favorite_form = FavoriteForm(request.POST or None)

    following = Following.objects.filter(following_id=profile_user.id)
    followers = Following.objects.filter(followed_id=profile_user.id)
    print(followers)
    selling = Product.objects.filter(seller_id=profile_user.id).exclude(sold=True)
    profile = UserProfile.objects.get(user=profile_user)

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
        follows=False
        for f in followers:
            print(user.username, " == ", f.following.username)
            if user.username == f.following.username:
                follows = True
                print("follows true")

        logged = UserProfile.objects.get(user=request.user)
        tparams = {"is_banned": is_banned,"user": user,'favorite_form': favorite_form,'favorites_ids': favorites, "profile_user": profile_user, "following": following, "followers": followers, "products": selling, 'profile': logged, "view_profile":profile, "follows":follows, "offer_count": getOffersCount(request), "report_form": report_form}
    else:
        tparams = {"is_banned": is_banned,"profile_user": profile_user, "following": following, "followers": followers,"products": selling,"view_profile":profile, "offer_count": getOffersCount(request)}

    return render(request, 'profile.html', tparams)

@login_required(login_url='/login/')
def pubProduct(request):
    if verifyIfAdmin(request):
        return redirect("/admin")
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        print(form.errors)
        if form.is_valid():
            print("form is valid")
            if request.user.is_authenticated:
                print("is authenticated")
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

                    if size in [30,31,32,33,34,35,36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,48]:
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
    if verifyIfAdmin(request):
        return redirect("/admin")
    form = SearchUserForm(request.POST or None)
    query = None
    all_users = None
    all_user_profiles = None
    myprofile = None
    if request.user.is_authenticated:
        myprofile = UserProfile.objects.get(user=request.user)

    popular_users = (
        User.objects.annotate(num_followers=Count('followers_set'))
        .order_by('-num_followers')[:10]
    )

    popular_users_profiles = UserProfile.objects.filter(user__in=popular_users)

    if request.method == 'POST' and form.is_valid():
        query = form.cleaned_data['query']
        all_users = User.objects.filter(username__icontains=query)
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
    if verifyIfAdmin(request):
        return redirect("/admin")
    error = ""
    product = Product.objects.get(id=id)
    report_form = ReportForm()
    print("product")
    print(product)
    if Jersey.objects.filter(product=product).exists():
        print("Cami")
        category = "camisola"
        p = Jersey.objects.get(product=product)
    elif Shorts.objects.filter(product=product).exists():
        print("Shor")
        category = "calções"
        p = Shorts.objects.get(product=product)
    elif Socks.objects.filter(product=product).exists():
        print("Mei")
        category = "meias"
        p = Socks.objects.get(product=product)
    elif Boots.objects.filter(product=product).exists():
        print("Chut")
        category = "chuteiras"
        p = Boots.objects.get(product=product)


    sellerProfile = UserProfile.objects.get(user = product.seller)
    try:
        user = User.objects.get(id=request.user.id)
        print(user)
        userProfile = UserProfile.objects.get(user__id=request.user.id)
        print(userProfile)
    except User.DoesNotExist or UserProfile.DoesNotExist:
        user = None
        userProfile = None
    if request.method == 'POST' and 'proposta' in request.POST:
        form = ListingOffer(userProfile, product, request.POST, request.FILES)
        if form.is_valid():
            print("valid")
            payment_method = form.cleaned_data['payment_method']
            delivery_method = form.cleaned_data['delivery_method']
            address = form.cleaned_data['custom_address']
            value = form.cleaned_data['value']
            buyer = userProfile
            sent_by = userProfile
            offer = Offer(buyer=buyer, product=product, value=value, address=address, payment_method=payment_method, delivery_method=delivery_method, sent_by=sent_by)
            if (payment_method == "store_credit"):
                buyer.wallet -= offer.value
                buyer.save()
            offer.save()
            return redirect('/')
    form = ListingOffer(userProfile, product)

    if request.user.is_authenticated:
        # Report form handling
        if request.method == 'POST' and 'report_product' in request.POST:
            report_form = ReportForm(request.POST)

            report_form.instance.sent_by = request.user
            report_form.instance.product = product
            if report_form.is_valid():
                report = report_form.save(commit=False)
                report.save()
                messages.success(request, 'Produto reportado com sucesso.')
                return redirect('detailedproduct',id=id)
            else:
                print("Form errors:", report_form.errors)
        else:
            report_form = ReportForm()
    else:
        error = "Login necessário"
    if user and user.id == p.product.seller.id:
        error = "Próprio produto"


    tparams = {"product": p, 'form': form, 'profile': userProfile, 'user' : user, 'offer_count' : getOffersCount(request), 'sellerProfile': sellerProfile, 'category': category, "report_form": report_form, "error": error}
    return render(request, 'productDetailed.html', tparams)

@login_required
def offers(request, action=None, id=None):
    if verifyIfAdmin(request):
        return redirect("/admin")
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
                    offer.sent_by = userProfile
                    offer.save()
                    print("saved")
        return redirect('/offers')
    form = ListingOffer(userProfile, None)
    madeOffers = Offer.objects.filter(sent_by__user_id=request.user.id).filter(offer_status__exact='in_progress')
    receivedOffers = Offer.objects.filter(product__seller_id=request.user.id) | Offer.objects.filter(buyer__user_id=request.user.id)
    receivedOffersFiltered = receivedOffers.exclude(sent_by__user_id=request.user.id).filter(offer_status__exact='in_progress')
    acceptedOffers = receivedOffers.filter(offer_status__exact='accepted').exclude(paid=True, delivered=True) | madeOffers.filter(offer_status__exact='accepted').exclude(paid=True, delivered=True)
    processedOffers = receivedOffers.filter(offer_status__exact='rejected') | madeOffers.filter(offer_status__exact='rejected') | Offer.objects.filter(paid=True, delivered=True, sent_by__user_id=request.user.id)
    tparams = {"profile": userProfile, "user": user, 'offers_received': receivedOffersFiltered, 'offers_made': madeOffers, 'offers_accepted': acceptedOffers, 'offers_processed': processedOffers, 'form': form, 'offer_count' : getOffersCount(request)}
    return render(request, 'offersTemplate.html', tparams)

def acceptOffer(request, id):
    return offers(request, 'accept', id)

def rejectOffer(request, id):
    return offers(request, 'reject', id)

def counterOffer(request, id):
    offer = Offer.objects.get(id=id)
    if offer.payment_method == "store_credit":
        if offer.sent_by.id != offer.buyer.id:
            offer.buyer.wallet -= offer.value
        else:
            offer.buyer.wallet += offer.value
        offer.buyer.save()
    return offers(request, 'counter', id)

def retractOffer(request, id):
    offer = Offer.objects.get(id=id)
    offer.delete()
    return redirect("/offers/")

def confirmPayment(request, id):
    offer = Offer.objects.get(id=id)
    offer.paid = not offer.paid
    offer.save()
    if offer.paid and offer.delivered:
        newOffer = Offer(buyer=offer.buyer, product=offer.product, value=offer.value,
                         payment_method=offer.payment_method, delivery_method=offer.delivery_method,
                         address=offer.address, sent_by=offer.buyer, offer_status=offer.offer_status,
                         delivered=offer.delivered, paid=offer.paid)
        if offer.buyer == offer.sent_by:
            userProfile = UserProfile.objects.get(user__id=offer.product.seller.id)
            newOffer = Offer(buyer=offer.buyer, product=offer.product, value=offer.value, payment_method=offer.payment_method, delivery_method=offer.delivery_method, address=offer.address, sent_by=userProfile, offer_status=offer.offer_status, delivered=offer.delivered, paid=offer.paid)
        newOffer.save()
    return redirect("/offers/")

def confirmDelivery(request, id):
    offer = Offer.objects.get(id=id)
    offer.delivered = not offer.delivered
    if offer.paid and offer.delivered:
        newOffer = Offer(buyer=offer.buyer, product=offer.product, value=offer.value,
                         payment_method=offer.payment_method, delivery_method=offer.delivery_method,
                         address=offer.address, sent_by=offer.buyer, offer_status=offer.offer_status,
                         delivered=offer.delivered, paid=offer.paid)
        if offer.buyer == offer.sent_by:
            userProfile = UserProfile.objects.get(user__id=offer.product.seller.id)
            newOffer = Offer(buyer=offer.buyer, product=offer.product, value=offer.value, payment_method=offer.payment_method, delivery_method=offer.delivery_method, address=offer.address, sent_by=userProfile, offer_status=offer.offer_status, delivered=offer.delivered, paid=offer.paid)
        newOffer.save()
    offer.save()
    return redirect("/offers/")

#Funções auxiliares
def valid_purchase(user : UserProfile, offer : Offer):
    return user.wallet < offer.value and not offer.product.sold

def perform_sale(buyer : UserProfile, seller : UserProfile, offer : Offer):
    if valid_purchase(buyer, offer):
        buyer.wallet -= offer.product.price
        seller.wallet += offer.product.price
        buyer.save()
        seller.save()
        return True
    return False


def getOffersCount(request):
    if request.user.is_authenticated:
        receivedOffers = Offer.objects.filter(product__seller_id=request.user.id) | Offer.objects.filter(buyer__user_id=request.user.id)
        receivedOffersFiltered = receivedOffers.exclude(sent_by__user_id=request.user.id).filter(offer_status__exact='in_progress')
        return receivedOffersFiltered.count()
    return 0

def notifySuccess(offer_id):
    offer = Offer.objects.get(id=offer_id)
    otherOffers = Offer.objects.filter(product_id=offer.product.id).exclude(id=offer.id)
    if (offer.payment_method == "store_credit" and offer.buyer.user.id != offer.sent_by.user.id):
        offer.buyer.wallet -= offer.value
    for otherOffer in otherOffers:
        otherOffer.offer_status = 'rejected'
        if (otherOffer.payment_method == "store_credit"):
            otherOffer.buyer.wallet += offer.value
            otherOffer.buyer.save()
        otherOffer.save()

    if offer.payment_method == "store_credit":
        seller = UserProfile.objects.get(user__id=offer.product.seller.id)
        seller.wallet += offer.value
        seller.save()

    offer.product.sold = True
    offer.product.save()
    offer.offer_status = 'accepted'
    offer.save()

def notifyFailed(offer_id):
    offer = Offer.objects.get(id=offer_id)
    if offer.payment_method == "store_credit" and offer.buyer.user.id == offer.sent_by.user.id:
        offer.buyer.wallet += offer.value
        offer.buyer.save()
    newOffer = Offer(buyer=offer.buyer, product=offer.product, value=offer.value,
                     payment_method=offer.payment_method, delivery_method=offer.delivery_method,
                     address=offer.address, sent_by=offer.buyer, offer_status=offer.offer_status,
                     delivered=offer.delivered, paid=offer.paid)
    if offer.buyer == offer.sent_by:
        seller = UserProfile.objects.get(user__id=offer.product.seller.id)
        newOffer = Offer(buyer=offer.buyer, product=offer.product, value=offer.value, payment_method=offer.payment_method, delivery_method=offer.delivery_method, address=offer.address, sent_by=seller, offer_status=offer.offer_status, delivered=offer.delivered, paid=offer.paid)
    newOffer.save()
    offer.offer_status = 'rejected'
    offer.save()

@login_required
def walletLogic(request):
    if verifyIfAdmin(request):
        return redirect("/admin")
    userinfo = UserProfile.objects.get(user=request.user)
    depositoform = DepositForm()
    levantamentoform = WithdrawalForm()

    return render(request, 'wallet.html', {
        'depositoform': depositoform,
        'levantamentoform': levantamentoform,
        'profile': userinfo,
        'offer_count': getOffersCount(request)
    })

@login_required
def deposit_money(request):
    if verifyIfAdmin(request):
        return redirect("/admin")
    userinfo = UserProfile.objects.get(user=request.user)
    depositoform = DepositForm(request.POST or None)

    if request.method == "POST" and depositoform.is_valid():
        deposit_amount = depositoform.cleaned_data['deposit_amount']
        userinfo.wallet += deposit_amount
        userinfo.save()
        return redirect('wallet')

    levantamentoform = WithdrawalForm()
    return render(request, 'wallet.html', {
        'depositoform': depositoform,
        'levantamentoform': levantamentoform,
        'profile': userinfo,
        'offer_count': getOffersCount(request)
    })

@login_required
def withdraw_money(request):
    if verifyIfAdmin(request):
        return redirect("/admin")
    userinfo = UserProfile.objects.get(user=request.user)
    levantamentoform = WithdrawalForm(request.POST or None)

    if request.method == "POST" and levantamentoform.is_valid():
        withdrawal_amount = levantamentoform.cleaned_data['withdrawal_amount']
        if withdrawal_amount <= userinfo.wallet:
            userinfo.wallet -= withdrawal_amount
            userinfo.save()
        return redirect('wallet')

    depositoform = DepositForm()
    return render(request, 'wallet.html', {
        'depositoform': depositoform,
        'levantamentoform': levantamentoform,
        'profile': userinfo,
        'offer_count': getOffersCount(request)
    })

@login_required
def account(request):
    if verifyIfAdmin(request):
        return redirect("/admin")
    image_form = UploadProfilePicture(request.POST)
    user = request.user
    account = UserProfile.objects.get(user=user)

    return render(request, 'account.html', {'user':user, 'account': account,'offer_count' : getOffersCount(request),'profile': UserProfile.objects.get(user=request.user)})

@login_required
def accountSettings(request):
    if verifyIfAdmin(request):
        return redirect("/admin")
    if request.method == 'GET':
        user = request.user
        account = UserProfile.objects.get(user=user)
        image_form = UploadProfilePicture()
        user_form = UpdateUser(initial={'email': user.email, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name})
        profile_form = UpdateProfile(initial={'address':account.address, 'phone':account.phone})
        password_form = UpdatePassword()
        return render(request, 'account.html', {'user': user, 'profile':account,'image_form': image_form, 'user_form': user_form,
                                                         'profile_form': profile_form, 'password_form': password_form,'offer_count' : getOffersCount(request)})
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
                    return render(request, 'account.html', {'user': user,'offer_count' : getOffersCount(request), 'profile':account, 'image_form': image_form})

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
                                                                     'success': 'Password changed successfully!','offer_count' : getOffersCount(request)})
                else:
                    print('Passwords do not match!')
                    return render(request, 'account.html', {'user': user, 'profile':account, 'password_form': password_form,
                                                                     'image_form': image_form,
                                                                     'profile_form': profile_form,
                                                                     'user_form': user_form,
                                                                     'error': 'Passwords do not match!','offer_count' : getOffersCount(request)})

            else:
                return render(request, 'account.html', {'user': user, 'profile':account, 'password_form': password_form,
                                                                 'image_form': image_form,
                                                                 'profile_form': profile_form,
                                                                 'user_form': user_form,
                                                                 'error': 'Invalid form!','offer_count' : getOffersCount(request)})


