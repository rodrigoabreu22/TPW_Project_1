from django.contrib import admin
from django.urls import path
from AmorCamisola import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('createaccount/', views.createAccount, name='createAccount'),

    path('publishproduct/', views.pubProduct, name='publishproduct'),

path('userprofile/', views.viewProfile, name='viewProfile'),
]
