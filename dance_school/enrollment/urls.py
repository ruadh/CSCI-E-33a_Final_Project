from django.urls import path

from . import views

urlpatterns = [
    # Authentication
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),


    # Navigation
    path('', views.index, name='index'),
    path('profile/<int:id>', views.profile_view, name='view_profile'),
    path('order/<int:id>', views.checkout, name='order'),
    path('contact-sheet/<int:id>', views.contact_sheet, name='contact_sheet'),

    # API
    path('users/<int:id>', views.profile, name='profile'),
    path('cart/<int:id>', views.update_cart, name='update_cart'),
]