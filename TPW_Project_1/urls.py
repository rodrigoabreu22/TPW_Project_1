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
    path('login/',auth_views.LoginView.as_view(template_name="login.html", next_page="myprofile"), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='publishproduct'), name='logout'),
    path('detailedproduct/<int:id>/', views.detailedProduct, name='detailedproduct'),
    path('',views.home, name='home'),
    path('follow/<str:username>/', views.follow_user, name='follow'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow'),

    path('acceptOffer/<int:id>/', views.acceptOffer, name='acceptOffer'),

    path('rejectOffer/<int:id>/', views.rejectOffer, name='rejectOffer'),
    path('offers/', views.offers, name='offers'),
    path('userlist/', views.userlist, name='userlist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)