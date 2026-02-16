from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.bus_signup, name="bus_signup"),
    path("verify-otp/", views.bus_verify_otp, name="bus_verify_otp"),
    path("login/", views.bus_login, name="bus_login"),
    path("forgot-password/", views.bus_forgot_password, name="bus_forgot_password"),
    path("reset-password/", views.bus_reset_password, name="bus_reset_password"),
    path("logout/", views.bus_logout, name="bus_logout"),
    path("dashboard/", views.bus_dashboard, name="bus_dashboard"),
    path("orders/", views.bus_orders, name="bus_orders"),
    path("add-bus/", views.add_bus, name="add_bus"),  
    path('orders/<int:order_id>/', views.order_detail_bus, name='bus_order_detail'),
    path('orders/history/<int:bus_id>/', views.bus_order_history, name='bus_order_history'),
    path('bus-partner/orders-history/', views.bus_partner_order_history, name='bus_partner_order_history'),

]
