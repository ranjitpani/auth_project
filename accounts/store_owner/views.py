from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .decorators import store_owner_required
from .forms import StoreForm, ProductForm, ProductStockFormSet
from accounts.models import Store, Product, CustomUser,OrderItem

# -------- Auth --------
def store_owner_login(request):
    if request.method == "POST":
        user = authenticate(email=request.POST["email"], password=request.POST["password"])
        if user and user.is_store_owner:
            login(request, user)
            return redirect("store_owner_dashboard")
        messages.error(request, "Invalid credentials")
    return render(request, "store_owner/login.html")

# def store_owner_signup(request):
#     if request.method == "POST":
#         email = request.POST["email"]
#         password = request.POST["password"]
#         if CustomUser.objects.filter(email=email).exists():
#             messages.error(request, "Email already exists")
#             return redirect("store_owner_login")
#         user = CustomUser.objects.create_user(email=email, password=password, is_store_owner=True)
#         login(request, user)
#         return redirect("store_owner_dashboard")
#     return render(request, "store_owner/signup.html")

from accounts.models import CustomUser
from accounts.models import EmailOTP
from accounts.utils import send_otp_email
from django.contrib.auth import login
from django.contrib import messages

def store_owner_signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm_password"]

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("store_owner_signup")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("store_owner_login")

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            is_store_owner=True,
            is_active=False   # 🔥 IMPORTANT
        )

        otp = EmailOTP.generate_otp()
        EmailOTP.objects.create(user=user, otp=otp)
        send_otp_email(email, otp)

        request.session["otp_user_id"] = user.id
        messages.success(request, "OTP sent to your email")
        return redirect("store_owner_verify_otp")

    return render(request, "store_owner/signup.html")

def store_owner_verify_otp(request):
    user_id = request.session.get("otp_user_id")

    if not user_id:
        return redirect("store_owner_signup")

    user = CustomUser.objects.get(id=user_id)

    if request.method == "POST":
        otp_input = request.POST["otp"]

        try:
            otp_obj = EmailOTP.objects.filter(user=user).latest("created_at")
        except EmailOTP.DoesNotExist:
            messages.error(request, "OTP not found")
            return redirect("store_owner_signup")

        if otp_obj.is_expired():
            messages.error(request, "OTP expired")
            return redirect("store_owner_signup")

        if otp_input == otp_obj.otp:
            user.is_active = True
            user.save()
            login(request, user)
            del request.session["otp_user_id"]
            messages.success(request, "Signup successful")
            return redirect("store_owner_dashboard")

        messages.error(request, "Invalid OTP")

    return render(request, "store_owner/verify_otp.html")



def store_owner_logout(request):
    logout(request)
    return redirect("store_owner_login")

# -------- Dashboard --------
@store_owner_required
def dashboard(request):
    stores = Store.objects.filter(owner=request.user)
    products = Product.objects.filter(store__owner=request.user)
    return render(request, "store_owner/dashboard.html", {
        "stores": stores,
        "products": products
    })

# -------- Store CRUD --------
@store_owner_required
def add_store(request):
    form = StoreForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        store = form.save(commit=False)
        store.owner = request.user
        store.save()
        messages.success(request, "Store created successfully")
        return redirect("store_owner_dashboard")
    return render(request, "store_owner/store_form.html", {"form": form})

@store_owner_required
def edit_store(request, id):
    store = get_object_or_404(Store, id=id, owner=request.user)
    form = StoreForm(request.POST or None, request.FILES or None, instance=store)
    if form.is_valid():
        form.save()
        messages.success(request, "Store updated successfully")
        return redirect("store_owner_dashboard")
    return render(request, "store_owner/store_form.html", {"form": form})

# -------- Product CRUD --------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProductForm, ProductStockFormSet, StoreForm
from accounts.models import Product, Store
from .decorators import store_owner_required

# --------------------------
# Add Product
# --------------------------
@store_owner_required
def add_product(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    form.fields['store'].queryset = Store.objects.filter(owner=request.user)
    stock_formset = ProductStockFormSet(request.POST or None)

    if form.is_valid() and stock_formset.is_valid():
        product = form.save(commit=False)
        # Auto GST from store if empty
        if not product.gst_number and product.store:
            product.gst_number = product.store.gst_number
        product.save()
        stock_formset.instance = product
        stock_formset.save()
        messages.success(request, "Product and stock added successfully")
        return redirect("store_owner_dashboard")

    return render(request, "store_owner/product_form.html", {
        "form": form,
        "stock_formset": stock_formset
    })


# --------------------------
# Edit Product
# --------------------------
@store_owner_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id, store__owner=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        form.fields['store'].queryset = Store.objects.filter(owner=request.user)

        stock_formset = ProductStockFormSet(
            request.POST,
            instance=product   # 🔥 THIS IS MUST
        )

        if form.is_valid() and stock_formset.is_valid():
            form.save()
            stock_formset.save()
            messages.success(request, "Product updated successfully")
            return redirect("store_owner_dashboard")
        else:
            print("FORM ERRORS:", form.errors)
            print("STOCK ERRORS:", stock_formset.errors)

    else:
        form = ProductForm(instance=product)
        form.fields['store'].queryset = Store.objects.filter(owner=request.user)

        stock_formset = ProductStockFormSet(
            instance=product   # 🔥 THIS IS MUST
        )

    return render(request, "store_owner/product_form.html", {
        "form": form,
        "stock_formset": stock_formset
    })
@store_owner_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id, store__owner=request.user)
    product.delete()
    messages.success(request, "Product deleted successfully")
    return redirect("store_owner_dashboard")

# store_owner/views.py

from accounts.models import OrderItem

@store_owner_required
def store_orders(request):
    orders = OrderItem.objects.select_related("order").filter(
        product__store__owner=request.user
    ).order_by("-order__created_at")

    return render(request, "store_owner/orders.html", {
        "orders": orders
    })

# store_owner/views.py

from accounts.models import Order

@store_owner_required
def mark_packed(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        items__product__store__owner=request.user
    )

    if order.status != "pending":
        messages.error(request, "You cannot update this order")
        return redirect("store_orders")

    order.status = "packed"
    order.save()

    messages.success(request, "Order marked as PACKED")
    return redirect("store_orders")

from django.http import JsonResponse
from accounts.models import OrderItem

@store_owner_required
def order_notification_count(request):
    count = OrderItem.objects.filter(
        product__store__owner=request.user,
        order__status="pending"
    ).count()

    return JsonResponse({
        "pending_count": count
    })