from django.urls import path
from .views import (
    signup, verify_otp, login_view, logout_view,
    forgot_password, verify_reset_otp, reset_password,
    home, cart, cart_history, location, profile
)

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
]