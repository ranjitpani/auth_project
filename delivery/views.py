from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import DeliverySignupForm
from .decorators import delivery_required
from accounts.models import Order

# 🔹 Signup
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from accounts.models import EmailOTP
from accounts.utils import generate_otp, send_otp_email
from .forms import DeliverySignupForm

def delivery_signup(request):
    if request.method == "POST":
        form = DeliverySignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_delivery_boy = True
            user.is_verified = False
            user.save()

            otp = generate_otp()
            EmailOTP.objects.create(user=user, otp=otp)

            # 📧 SEND OTP (Resend)
            send_otp_email(user.email, otp, purpose="verify")

            request.session["verify_user_id"] = user.id
            messages.success(request, "OTP sent to your email")
            return redirect("delivery-signup-verify-otp")
    else:
        form = DeliverySignupForm()

    return render(request, "delivery/signup.html", {"form": form})
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from accounts.models import EmailOTP

User = get_user_model()
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect
from accounts.models import CustomUser

# def delivery_verify_signup_otp(request):
#     if request.method == "POST":
#         otp = request.POST.get("otp")

#         user_id = request.session.get("delivery_user_id")
#         if not user_id:
#             messages.error(request, "Session expired. Signup again.")
#             return redirect("delivery-signup")

#         user = CustomUser.objects.filter(
#             id=user_id,
#             is_delivery=True
#         ).first()

#         if not user:
#             messages.error(request, "User not found")
#             return redirect("delivery-signup")

#         if user.otp != otp:
#             messages.error(request, "Invalid OTP")
#             return redirect("delivery-signup-verify-otp")

#         # ✅ OTP correct
#         user.is_verified = True
#         user.otp = None
#         user.save()

#         # ✅ LOGIN DELIVERY BOY
#         login(request, user)

#         # ✅ CLEAN SESSION
#         request.session.pop("delivery_user_id", None)

#         messages.success(request, "Account verified successfully")
#         return redirect("delivery-dashboard")

#     return render(request, "delivery/verify_otp.html")
def delivery_verify_signup_otp(request):
    user_id = request.session.get("verify_user_id")
    if not user_id:
        messages.error(request, "Session expired. Signup again.")
        return redirect("delivery-signup")

    user = CustomUser.objects.filter(
        id=user_id,
        is_delivery_boy=True
    ).first()

    if not user:
        messages.error(request, "User not found")
        return redirect("delivery-signup")

    if request.method == "POST":
        otp = request.POST.get("otp")
        email_otp_obj = EmailOTP.objects.filter(user=user, otp=otp).first()
        if not email_otp_obj:
            messages.error(request, "Invalid OTP")
            return redirect("delivery-signup-verify-otp")

        # OTP correct
        user.is_verified = True
        user.save()

        # Delete OTP object
        email_otp_obj.delete()

        # Login delivery boy
        login(request, user)

        # ✅ safe session delete
        request.session.pop("verify_user_id", None)

        messages.success(request, "Account verified successfully")
        return redirect("delivery-dashboard")

    return render(request, "delivery/verify_otp.html")
# 🔹 Login
def delivery_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user and user.is_delivery_boy:
            login(request, user)
            return redirect("delivery-dashboard")
    return render(request, "delivery/login.html")

from django.contrib.auth import get_user_model
from accounts.utils import generate_otp, send_otp_email
from django.contrib import messages

User = get_user_model()
def delivery_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = CustomUser.objects.filter(email=email, is_delivery_boy=True).first()
        if not user:
            messages.error(request, "User not found")
            return redirect("delivery-forgot-password")
        otp = generate_otp()
        EmailOTP.objects.update_or_create(user=user, defaults={"otp": otp})
        send_otp_email(user.email, otp, purpose="forgot")
        request.session["delivery_forgot_user_id"] = user.id
        messages.success(request, "OTP sent to your email. Verify and reset password.")
        return redirect("delivery-reset-password")  # <-- redirect now valid
    return render(request, "delivery/forgot_password.html")

from accounts.models import CustomUser
from django.contrib import messages

def delivery_reset_password(request):
    user_id = request.session.get("delivery_forgot_user_id")
    if not user_id:
        messages.error(request, "Session expired. Try forgot password again.")
        return redirect("delivery-forgot-password")

    user = CustomUser.objects.filter(id=user_id, is_delivery_boy=True).first()
    if not user:
        messages.error(request, "User not found")
        return redirect("delivery-forgot-password")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("delivery-reset-password")
        user.set_password(password)
        user.save()
        messages.success(request, "Password reset successful. Login now.")
        # clean session
        request.session.pop("delivery_forgot_user_id", None)
        return redirect("delivery-login")

    return render(request, "delivery/reset_password.html")


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import Order
from accounts.utils import send_otp_email

# 🔹 Dashboard
# @login_required
# @delivery_required
# def delivery_dashboard(request):
#     orders = Order.objects.filter(
#         delivery_boy=request.user,
#         status__in=["assigned", "accepted", "out_for_delivery"]
#     )
#     return render(request, "delivery/dashboard.html", {"orders": orders})
@login_required
@delivery_required
def delivery_dashboard(request):
    # Only show orders for this delivery boy
    orders = Order.objects.filter(
        delivery_boy=request.user,
        status__in=["assigned", "accepted", "out_for_delivery"]
    ).order_by("-id")  # newest first
    return render(request, "delivery/dashboard.html", {"orders": orders})

@login_required
def accept_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        delivery_boy=request.user
    )

    order.status = "accepted"
    order.generate_otp()   # 🔥 OTP generate
    order.save()

    # ✅ OTP USER EMAIL ku patha
    send_otp_email(
        order.user.email,
        order.delivery_otp,
        purpose="verify"
    )

    return redirect("delivery-store-route", order.id)


from django.shortcuts import get_object_or_404, render
from accounts.models import Order
from django.contrib.auth.decorators import login_required

@login_required
def delivery_store_route(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # 🔥 Get store via order item
    item = order.items.select_related("product__store").first()
    store = item.product.store

    context = {
        "order": order,
        "store_lat": store.latitude,
        "store_lng": store.longitude,
    }
    return render(request, "delivery/store_route.html", context)

@login_required
def pickup_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        delivery_boy=request.user
    )

    order.status = "picked_up"
    order.save()

    return redirect("delivery-user-route", order.id)

@login_required
def delivery_user_route(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        delivery_boy=request.user
    )

    order.status = "out_for_delivery"
    order.save()

    return render(request, "delivery/user_route.html", {
        "order": order,
        "user_lat": order.latitude,
        "user_lng": order.longitude,
    })



from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

@login_required
def delivery_order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        delivery_boy=request.user
    )

    return render(request, "delivery/order_detail.html", {
        "order": order
    })

@login_required
def reject_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        delivery_boy=request.user
    )
    order.status = "rejected"
    order.delivery_boy = None
    order.save()
    return redirect("delivery-dashboard")

@login_required
def verify_delivery_otp(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        delivery_boy=request.user
    )

    if request.method == "POST":
        otp = request.POST.get("otp")

        if otp == order.delivery_otp:
            order.otp_verified = True
            order.status = "delivered"
            order.save()
            return redirect("delivery-dashboard")

    return render(request, "delivery/verify_otp.html", {"order": order})

from django.http import JsonResponse

@login_required
@delivery_required
def delivery_dashboard_orders_json(request):
    orders = Order.objects.filter(
        delivery_boy=request.user,
        status__in=["assigned", "accepted", "out_for_delivery"]
    ).values("id", "status", "order_uid").order_by("-id")
    return JsonResponse({"orders": list(orders)})

# 🔹 Logout
def delivery_logout(request):
    logout(request)
    return redirect("delivery-login")

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from accounts.models import Order

@login_required
def delivery_history(request):
    today = timezone.now().date()

    # ✅ All completed deliveries (history)
    orders = Order.objects.filter(
        delivery_boy=request.user,
        status="delivered"
    ).order_by("-created_at")

    # ✅ Today completed deliveries
    today_orders = orders.filter(created_at__date=today)

    context = {
        "orders": orders,
        "today_total": today_orders.count(),
        "today_normal": today_orders.filter(return_type="normal").count(),
        "today_return": today_orders.filter(return_type="return").count(),
        "today_refund": today_orders.filter(return_type="refund").count(),
        "today_exchange": today_orders.filter(return_type="exchange").count(),
    }

    return render(request, "delivery/delivery_history.html", context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import Order
from django.utils import timezone

@login_required
def delivery_calendar(request):
    user = request.user
    selected_date = request.GET.get('date')  # ?date=YYYY-MM-DD
    if selected_date:
        try:
            selected_date = timezone.datetime.strptime(selected_date, "%Y-%m-%d").date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    # All completed orders for this user
    completed_orders = Order.objects.filter(delivery_boy=user, status="delivered")

    # Orders for the selected date
    date_orders = completed_orders.filter(created_at__date=selected_date)

    context = {
    "selected_date": selected_date,
    "date_orders": date_orders,
    "total_orders": date_orders.count(),
    "total_normal": date_orders.filter(return_type="normal").count(),
    "total_return": date_orders.filter(return_type="return").count(),
    "total_refund": date_orders.filter(return_type="refund").count(),
    "total_exchange": date_orders.filter(return_type="exchange").count(),
}
    return render(request, "delivery/delivery_calendar.html", context)

from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

@login_required
def delivery_analytics(request):
    user = request.user
    today = timezone.now().date()

    # WEEKLY
    week_start = today - timedelta(days=6)
    weekly = (
        Order.objects.filter(
            delivery_boy=user,
            status="delivered",
            created_at__date__range=[week_start, today]
        )
        .extra(select={'day': "date(created_at)"})
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

    # MONTHLY
    monthly = (
        Order.objects.filter(
            delivery_boy=user,
            status="delivered",
            created_at__month=today.month,
            created_at__year=today.year
        )
        .extra(select={'day': "date(created_at)"})
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

    return JsonResponse({
        "weekly": list(weekly),
        "monthly": list(monthly)
    })
