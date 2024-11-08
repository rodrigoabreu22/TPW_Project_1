from django.contrib import admin
from django.urls import path
from AmorCamisola import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('createaccount/', views.createAccount, name='createaccount'),
    path('myprofile/', views.myProfile, name='myprofile'),

    path('profile/<str:username>', views.viewProfile, name='profile'),
    path('publishproduct/', views.pubProduct, name='publishproduct'),
    path('login/',auth_views.LoginView.as_view(template_name="login.html", next_page="home"), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('',views.home, name='home'),
    path('follow/<str:username>/', views.follow_user, name='follow'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow'),
    path('userlist/', views.userlist, name='userlist'),
    path('wallet/', views.walletLogic, name='wallet'),
    path('wallet/deposit/', views.deposit_money, name='deposit_money'),
    path('wallet/withdraw/', views.withdraw_money, name='withdraw_money'),
    path('myprofile/settings', views.accountSettings, name='profile_settings'),  # Profile page
    path('favorites/', views.favorite_list, name='favorite_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)