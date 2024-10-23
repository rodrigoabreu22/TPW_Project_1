from django.contrib import admin
from django.urls import path
from AmorCamisola import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),

    path('books/', views.books, name='books'),

    path('books/<int:id>/', views.bookDetails, name='bookDetails'),

    path('authors/', views.authors, name='authors'),

    path('authors/<int:id>/', views.authorDetails, name='authorDetails'),

    path('publishers/', views.publishers, name='publishers'),

    path('publishers/<int:id>/', views.publisherDetails, name='publisherDetails'),

    path('author/<int:author_id>/books', views.booksByAuthor, name='booksByAuthor'),

    path('publishers/<int:pub_id>/authors', views.publisherAuthors, name='publisherAuthors'),

    path('booksearch/', views.booksearch, name='booksearch'),

    path('authorsearch/', views.searchAuthor2, name='authorsearch'),

    path('booksearchAP/', views.booksearchAP2, name='booksearchAP'),

    path('insertauthor/', views.insertAuthor2, name='insertAuthor'),

    path('insertpublisher/', views.insertPublisher2, name='insertPublisher'),

    path('insertbook/', views.insertBook2, name='insertBook'),

    path('bookquery/', views.bookquery, name='bookquery'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    path('logout', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('cart', views.purchased_books, name='cart'),

    path('buy_book/<int:id>', views.buy_book, name='buy_book'),
]
