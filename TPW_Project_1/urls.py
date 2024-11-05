from django.contrib import admin
from django.urls import path
from AmorCamisola import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('createaccount/', views.createAccount, name='createaccount'),
    path('userprofile/', views.viewProfile, name='viewProfile'),
    path('publishproduct/', views.pubProduct, name='publishproduct'),
    path('login/',auth_views.LoginView.as_view(template_name="login.html", next_page="viewProfile"), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='publishproduct'), name='logout'),
    path('',views.home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)