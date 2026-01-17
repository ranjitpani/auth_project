from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.delivery_signup, name="delivery-signup"),
    path("verify-otp/", views.delivery_verify_signup_otp, name="delivery-signup-verify-otp"),
    path("login/", views.delivery_login, name="delivery-login"),
    path("delivery/forgot-password/", views.delivery_forgot_password, name="delivery-forgot-password"),
    path("reset-password/", views.delivery_reset_password, name="delivery-reset-password"),
    path("dashboard/", views.delivery_dashboard, name="delivery-dashboard"),
    path("logout/", views.delivery_logout, name="delivery-logout"),
    path("order/<int:order_id>/accept/", views.accept_order, name="delivery-accept"),
    path("order/<int:order_id>/reject/", views.reject_order, name="delivery-reject"),
    path("order/<int:order_id>/verify-otp/", views.verify_delivery_otp, name="delivery-verify-otp"),
    path(
    "order/<int:order_id>/store-route/",
    views.delivery_store_route,
    name="delivery-store-route"
),
path(
        "order/<int:order_id>/detail/",
        views.delivery_order_detail,
        name="delivery-order-detail"
    ),
    path(
    "order/<int:order_id>/pickup/",
    views.pickup_order,
    name="delivery-pickup"
),
path(
    "order/<int:order_id>/user-route/",
    views.delivery_user_route,
    name="delivery-user-route"
),
path("delivery/history/", views.delivery_history, name="delivery-history"),
path("calendar/", views.delivery_calendar, name="delivery-calendar"),
path("delivery/analytics/", views.delivery_analytics, name="delivery-analytics"),
path('dashboard/orders-json/', views.delivery_dashboard_orders_json, name="delivery-dashboard-orders-json"),
]