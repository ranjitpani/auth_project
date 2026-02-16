from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login
from accounts.utils import generate_otp



# ================= SIGNUP =================
from django.shortcuts import render, redirect
from accounts.utils import generate_otp, send_otp_email
from accounts.models import EmailOTP
from django.contrib.auth import get_user_model

User = get_user_model()

def bus_signup(request):

    if request.method == "POST":
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "bus_partner/signup.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(email=email).exists():
            return render(request, "bus_partner/signup.html", {
                "error": "Email already registered"
            })

        otp = generate_otp()

        # Save data temporarily in session
        request.session["signup_data"] = {
            "email": email,
            "first_name": first_name,
            "password": password,
            "otp": otp,
        }

        send_otp_email(email, otp)

        return redirect("bus_verify_otp")

    return render(request, "bus_partner/signup.html")
from django.contrib.auth import login

def bus_verify_otp(request):

    signup_data = request.session.get("signup_data")

    if not signup_data:
        return redirect("bus_signup")

    if request.method == "POST":
        otp_entered = request.POST.get("otp")

        if otp_entered != signup_data["otp"]:
            return render(request, "bus_partner/verify_otp.html", {
                "error": "Invalid OTP"
            })

        # ✅ CREATE USER HERE (AFTER OTP SUCCESS)
        user = User.objects.create(
            email=signup_data["email"],
            first_name=signup_data["first_name"],
            is_bus_partner=True,
            is_verified=True
        )

        user.set_password(signup_data["password"])
        user.save()

        # Clear session
        del request.session["signup_data"]

        login(request, user)

        return redirect("bus_dashboard")

    return render(request, "bus_partner/verify_otp.html")


# ================= LOGIN =================
def bus_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user and user.is_bus_partner and user.is_verified:
            login(request, user)
            return redirect("bus_dashboard")

        return render(request, "bus_partner/login.html", {
            "error": "Invalid credentials or account not verified"
        })

    return render(request, "bus_partner/login.html")


# ================= FORGOT PASSWORD =================
from accounts.models import PasswordResetOTP
from accounts.utils import generate_otp, send_otp_email

def bus_forgot_password(request):

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email, is_bus_partner=True)

            otp = generate_otp()

            # Delete old OTP
            PasswordResetOTP.objects.filter(user=user).delete()

            # Save OTP
            PasswordResetOTP.objects.create(user=user, otp=otp)

            send_otp_email(email, otp)

            request.session["reset_email"] = email

            return redirect("bus_reset_password")

        except User.DoesNotExist:
            return render(request, "bus_partner/forgot_password.html", {
                "error": "Email not found"
            })

    return render(request, "bus_partner/forgot_password.html")

# ================= RESET PASSWORD =================
from accounts.models import PasswordResetOTP

def bus_reset_password(request):

    email = request.session.get("reset_email")

    if not email:
        return redirect("bus_forgot_password")

    if request.method == "POST":

        otp_entered = request.POST.get("otp")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        user = User.objects.get(email=email)
        otp_obj = PasswordResetOTP.objects.filter(user=user).last()

        if not otp_obj:
            return render(request, "bus_partner/reset_password.html", {
                "error": "OTP expired"
            })

        # STEP 1 → OTP VERIFY
        if otp_entered and not password:

            if not otp_obj.is_valid():
                otp_obj.delete()
                return render(request, "bus_partner/reset_password.html", {
                    "error": "OTP expired"
                })

            if otp_obj.otp != otp_entered:
                return render(request, "bus_partner/reset_password.html", {
                    "error": "Invalid OTP"
                })

            return render(request, "bus_partner/reset_password.html", {
                "show_password_fields": True
            })

        # STEP 2 → PASSWORD CHANGE
        if password:

            if password != confirm_password:
                return render(request, "bus_partner/reset_password.html", {
                    "show_password_fields": True,
                    "error": "Passwords do not match"
                })

            user.set_password(password)
            user.save()

            otp_obj.delete()
            del request.session["reset_email"]

            return redirect("bus_login")

    return render(request, "bus_partner/reset_password.html")

from django.contrib.auth import logout
from django.shortcuts import redirect

def bus_logout(request):
    logout(request)
    return redirect("bus_login")
from accounts.models import Order
from .decorators import bus_partner_required


from accounts.models import Bus, Order

@bus_partner_required
def bus_dashboard(request):

    orders = Order.objects.filter(bus_partner=request.user)

    buses = Bus.objects.filter(partner=request.user)

    return render(request, "bus_partner/dashboard.html", {
        "orders": orders,
        "buses": buses
    })


from accounts.models import Bus


@bus_partner_required
def add_bus(request):
    if request.method == "POST":
        Bus.objects.create(
            partner=request.user,
            bus_name=request.POST.get("bus_name"),
            number_plate=request.POST.get("number_plate"),
            mobile_number=request.POST.get("mobile_number"),
            route_district=request.POST.get("route_district"),
            route_block=request.POST.get("route_block"),
            arrival_time=request.POST.get("arrival_time"),
        )
        return redirect("bus_dashboard")

    return render(request, "bus_partner/add_bus.html")

@bus_partner_required
def bus_orders(request):
    orders = Order.objects.filter(
        bus_partner=request.user,
        status="assigned"
    )

    return render(request, "bus_partner/bus_orders.html", {
        "orders": orders
    })


from accounts.models import Bus, Order
from django.shortcuts import render, get_object_or_404, redirect

@bus_partner_required
def order_detail_bus(request, order_id):
    order = get_object_or_404(Order, id=order_id, bus_partner=request.user)

    # Ensure delivery_block is string
    order.delivery_block = (order.delivery_block or "").strip()

    # Filter buses based on block
    buses = Bus.objects.filter(
        partner=request.user,
        route_block__iexact=order.delivery_block
    )

    if request.method == "POST":
        bus_id = request.POST.get("bus_id")  # get selected bus from form
        if not bus_id:
            return render(request, "bus_partner/order_detail.html", {
                "order": order,
                "buses": buses,
                "error": "No bus selected"
            })
        
        bus = get_object_or_404(Bus, id=bus_id, partner=request.user)

        order.bus = bus
        order.bus_name = bus.bus_name
        order.bus_number_plate = bus.number_plate
        order.bus_mobile = bus.mobile_number
        order.status = "shipped"
        order.save()

        return redirect("bus_orders")

    return render(request, "bus_partner/order_detail.html", {
        "order": order,
        "buses": buses
    })


from django.shortcuts import render, get_object_or_404
from accounts.models import Order, Bus

def bus_order_history(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    orders = Order.objects.filter(bus_partner=bus.partner, bus_name=bus.bus_name).order_by('-created_at')
    
    context = {
        'bus': bus,
        'orders': orders,
    }
    return render(request, 'bus_partner/bus_order_history.html', context)

from django.shortcuts import render

from django.utils.dateparse import parse_date

def bus_partner_order_history(request):
    user = request.user
    orders = Order.objects.filter(bus_partner=user).order_by('-created_at')

    # 🔹 Date filter
    selected_date = request.GET.get('date')
    if selected_date:
        # Parse string to date
        date_obj = parse_date(selected_date)
        if date_obj:
            orders = orders.filter(created_at__date=date_obj)

    context = {
        'orders': orders,
        'selected_date': selected_date
    }
    return render(request, 'bus_partner/order_history.html', context)
