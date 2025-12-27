from django.urls import path
from .views import (
    signup, verify_otp, login_view, logout_view,
    forgot_password, verify_reset_otp, reset_password,
    home, cart, cart_history, location, profile,
    load_states, load_districts, load_blocks, store_detail,
    product_detail, add_to_cart, buy_now  # <-- new views
)
from accounts.views import create_superuser
urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-reset-otp/', verify_reset_otp, name='verify_reset_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('cart/', cart, name='cart'),
    path('cart-history/', cart_history, name='cart_history'),
    path('location/', location, name='location'),
    path('profile/', profile, name='profile'),

    # AJAX endpoints for dynamic location dropdown
    path('ajax/load-states/', load_states, name='ajax_load_states'),
    path('ajax/load-districts/', load_districts, name='ajax_load_districts'),
    path('ajax/load-blocks/', load_blocks, name='ajax_load_blocks'),

    # Store detail
    path('store/<int:id>/', store_detail, name='store_detail'),

    # Product actions
    path('product/<int:id>/', product_detail, name='product_detail'),
    path('add-to-cart/<int:id>/', add_to_cart, name='add_to_cart'),
    path('buy-now/<int:id>/', buy_now, name='buy_now'),
    path('create-superuser/', create_superuser),
]