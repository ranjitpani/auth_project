from django.urls import path
from .views import *

urlpatterns = [
    path("login/", store_owner_login, name="store_owner_login"),
    path("signup/", store_owner_signup, name="store_owner_signup"),

    # 🔐 Forgot password
    path("forgot-password/", store_owner_forgot_password, name="store_owner_forgot_password"),
    path("forgot-verify-otp/", store_owner_forgot_verify_otp, name="store_owner_forgot_verify_otp"),
    path("reset-password/", store_owner_reset_password, name="store_owner_reset_password"),

    # 🔐 Signup OTP
    path("signup-verify-otp/", store_owner_verify_otp, name="store_owner_verify_otp"),

    path("logout/", store_owner_logout, name="store_owner_logout"),
    path("dashboard/", dashboard, name="store_owner_dashboard"),

    path("store/add/", add_store, name="add_store"),
    path("store/<int:id>/edit/", edit_store, name="edit_store"),

    path("orders/", store_orders, name="store_orders"),
    path("orders/<int:order_id>/packed/", mark_packed, name="mark_packed"),

    path("product/add/", add_product, name="add_product"),
    path("product/<int:id>/edit/", edit_product, name="edit_product"),
    path("product/<int:id>/delete/", delete_product, name="delete_product"),

    path("orders/notification-count/", order_notification_count, name="order_notification_count"),
]