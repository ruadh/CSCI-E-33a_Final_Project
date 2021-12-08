from django.urls import path

from . import views

urlpatterns = [
    # Authentication
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),


    # Navigation
    path('', views.index, name='index'),
    # path('posts', views.save_post, name='new_post'),
    # path('following', views.following_posts, name='following'),
    path('users/<int:id>', views.view_profile, name='view_profile'),
    path('contact-sheet/<int:id>', views.contact_sheet, name='contact_sheet'),
    # path('offerings/<int:id>', views.view_offering, name='view_offering'),

    # # API
    path('cart/<int:id>', views.update_cart, name='update_cart'),
    path('checkout/<int:id>', views.checkout_preview, name='checkout'),
    # path('likes/<int:id>', views.toggle_like, name='toggle_like'),
    # path('follows/<int:id>', views.toggle_follow, name='toggle_follow'),
]