# from django.urls import path
# from .views import (
#     signup, verify_otp, login_view, logout_view,
#     forgot_password, verify_reset_otp, reset_password,
#     home, cart, cart_history, location, profile,
#     load_states, load_districts, load_blocks, store_detail,
#     product_detail, add_to_cart, buy_now , remove_from_cart,update_cart_quantity,increase_qty,decrease_qty,
#      place_order,live_search,checkout_address,checkout_payment,checkout_summary,save_address,change_address,edit_address,cancel_order,order_detail,request_order_action,ajax_load_villages,download_invoice,product_invoice  # <-- new views

# )
# from accounts.views import create_superuser
# urlpatterns = [
#     path('', home, name='home'),
#     path('signup/', signup, name='signup'),
#     path('verify-otp/', verify_otp, name='verify_otp'),
#     path('login/', login_view, name='login'),
#     path('logout/', logout_view, name='logout'),
#     path('forgot-password/', forgot_password, name='forgot_password'),
#     path('verify-reset-otp/', verify_reset_otp, name='verify_reset_otp'),
#     path('reset-password/', reset_password, name='reset_password'),
#     path('cart/', cart, name='cart'),
#     path('cart-history/', cart_history, name='cart_history'),
#     path('location/', location, name='location'),
#     path('profile/', profile, name='profile'),

#     # AJAX endpoints for dynamic location dropdown
#     path('ajax/load-states/', load_states, name='ajax_load_states'),
#     path('ajax/load-districts/', load_districts, name='ajax_load_districts'),
#     path('ajax/load-blocks/', load_blocks, name='ajax_load_blocks'),

#     # Store detail
#     path('store/<int:id>/', store_detail, name='store_detail'),

#     # Product actions
#     path('product/<int:id>/', product_detail, name='product_detail'),
#     # urls.py
# # path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
# # path('buy-now/<int:product_id>/', buy_now, name='buy_now'),
# # old
# # path('add-to-cart/<int:id>/', add_to_cart, name='add_to_cart'),

# # new (size included)
# path('add-to-cart/<int:product_id>/<str:size>/', add_to_cart, name='add_to_cart'),
# path('buy-now/<int:product_id>/<str:size>/', buy_now, name='buy_now'),
#     path('create-superuser/', create_superuser),
#     path('cart/remove/<int:product_id>/<str:size>/', remove_from_cart, name='remove_from_cart'),
# path('cart/update/<int:product_id>/<str:size>/', update_cart_quantity, name='update_cart_quantity'),
# path('cart/increase/<int:product_id>/<str:size>/', increase_qty, name='increase_qty'),
# path('cart/decrease/<int:product_id>/<str:size>/', decrease_qty, name='decrease_qty'),
# path('place-order/', place_order, name='place_order'),
# path('ajax/live-search/', live_search, name='live_search'),
# path('ajax/store-live-search/<int:id>/', store_detail, name='ajax_store_live_search'),
# path('checkout/address/', checkout_address, name='checkout_address'),
# path('checkout/summary/', checkout_summary, name='checkout_summary'),
# path('checkout/payment/', checkout_payment, name='checkout_payment'),
# path('checkout/save-address/', save_address, name='save_address'),
# path('checkout/change-address/', change_address, name='change_address'),
#  path('checkout/edit-address/<int:address_id>/', edit_address, name='edit_address'),
#  path('order/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
#  path('order/<int:order_id>/',order_detail, name='order_detail'),
#  path('order-action/<int:item_id>/<str:action>/',request_order_action, name='request_order_action'),
#  path('ajax/load-villages/', ajax_load_villages, name='ajax_load_villages'),
#  path(
#         "order/<int:order_id>/invoice/",
#        download_invoice,
#         name="download_invoice"
#     ),
# path(
#     "invoice/product/<int:item_id>/",
#     product_invoice,
#     name="product_invoice"
# ),    



   
# ]

from django.urls import path
from .views import (
    signup, verify_otp, login_view, logout_view,
    forgot_password, verify_reset_otp, reset_password,
    home, cart, cart_history, location, profile,
    load_states, load_districts, load_blocks, store_detail,
    product_detail, add_to_cart, buy_now , remove_from_cart,
    update_cart_quantity, increase_qty, decrease_qty,
    place_order, live_search, checkout_address, checkout_payment,
    checkout_summary, save_address, change_address, edit_address,
    cancel_order, order_detail, request_order_action, ajax_load_villages,
    download_invoice, product_invoice,
 # <-- added store owner views
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
    path('add-to-cart/<int:product_id>/<str:size>/', add_to_cart, name='add_to_cart'),
    path('buy-now/<int:product_id>/<str:size>/', buy_now, name='buy_now'),

    # Cart actions
    path('cart/remove/<int:product_id>/<str:size>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/<str:size>/', update_cart_quantity, name='update_cart_quantity'),
    path('cart/increase/<int:product_id>/<str:size>/', increase_qty, name='increase_qty'),
    path('cart/decrease/<int:product_id>/<str:size>/', decrease_qty, name='decrease_qty'),

    # Order
    path('place-order/', place_order, name='place_order'),
    path('ajax/live-search/', live_search, name='live_search'),
    path('ajax/store-live-search/<int:id>/', store_detail, name='ajax_store_live_search'),

    # Checkout
    path('checkout/address/', checkout_address, name='checkout_address'),
    path('checkout/summary/', checkout_summary, name='checkout_summary'),
    path('checkout/payment/', checkout_payment, name='checkout_payment'),
    path('checkout/save-address/', save_address, name='save_address'),
    path('checkout/change-address/', change_address, name='change_address'),
    path('checkout/edit-address/<int:address_id>/', edit_address, name='edit_address'),

    # Order actions
    path('order/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('order-action/<int:item_id>/<str:action>/', request_order_action, name='request_order_action'),

    # AJAX villages
    path('ajax/load-villages/', ajax_load_villages, name='ajax_load_villages'),

    # Invoices
    path('order/<int:order_id>/invoice/', download_invoice, name='download_invoice'),
    path('invoice/product/<int:item_id>/', product_invoice, name='product_invoice'),

    # Admin
    path('create-superuser/', create_superuser),


]