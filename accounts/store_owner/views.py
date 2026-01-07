# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages
# from .decorators import store_owner_required
# from .forms import StoreForm, ProductForm, ProductStockFormSet
# from accounts.models import Store, Product, CustomUser,OrderItem
# from django.shortcuts import render, redirect
# from django.contrib import messages

# from django.contrib.auth.hashers import make_password
# from accounts.models import PasswordResetOTP
# from accounts.utils import generate_otp
# # -------- Auth --------
# def store_owner_login(request):
#     if request.method == "POST":
#         user = authenticate(email=request.POST["email"], password=request.POST["password"])
#         if user and user.is_store_owner:
#             login(request, user)
#             return redirect("store_owner_dashboard")
#         messages.error(request, "Invalid credentials")
#     return render(request, "store_owner/login.html")

# # def store_owner_signup(request):
# #     if request.method == "POST":
# #         email = request.POST["email"]
# #         password = request.POST["password"]
# #         if CustomUser.objects.filter(email=email).exists():
# #             messages.error(request, "Email already exists")
# #             return redirect("store_owner_login")
# #         user = CustomUser.objects.create_user(email=email, password=password, is_store_owner=True)
# #         login(request, user)
# #         return redirect("store_owner_dashboard")
# #     return render(request, "store_owner/signup.html")

# from accounts.models import CustomUser
# from accounts.models import EmailOTP

# from django.contrib.auth import login
# from django.contrib import messages

# def store_owner_signup(request):
#     if request.method == "POST":
#         email = request.POST["email"]
#         password = request.POST["password"]
#         confirm = request.POST["confirm_password"]

#         if password != confirm:
#             messages.error(request, "Passwords do not match")
#             return redirect("store_owner_signup")

#         if CustomUser.objects.filter(email=email).exists():
#             messages.error(request, "Email already exists")
#             return redirect("store_owner_login")

#         user = CustomUser.objects.create_user(
#             email=email,
#             password=password,
#             is_store_owner=True,
#             is_active=False   # 🔥 IMPORTANT
#         )

#         otp = EmailOTP.generate_otp()
#         EmailOTP.objects.create(user=user, otp=otp)
#         send_otp_email(email, otp)

#         request.session["otp_user_id"] = user.id
#         messages.success(request, "OTP sent to your email")
#         return redirect("store_owner_verify_otp")

#     return render(request, "store_owner/signup.html")

# def store_owner_verify_otp(request):
#     user_id = request.session.get("otp_user_id")

#     if not user_id:
#         return redirect("store_owner_signup")

#     user = CustomUser.objects.get(id=user_id)

#     if request.method == "POST":
#         otp_input = request.POST["otp"]

#         try:
#             otp_obj = EmailOTP.objects.filter(user=user).latest("created_at")
#         except EmailOTP.DoesNotExist:
#             messages.error(request, "OTP not found")
#             return redirect("store_owner_signup")

#         if otp_obj.is_expired():
#             messages.error(request, "OTP expired")
#             return redirect("store_owner_signup")

#         if otp_input == otp_obj.otp:
#             user.is_active = True
#             user.save()
#             login(request, user)
#             del request.session["otp_user_id"]
#             messages.success(request, "Signup successful")
#             return redirect("store_owner_dashboard")

#         messages.error(request, "Invalid OTP")

#     return render(request, "store_owner/verify_otp.html")

# from django.contrib.auth import get_user_model
# User = get_user_model()


# # def store_owner_forgot_password(request):
# #     if request.method == "POST":
# #         email = request.POST.get("email")

# #         try:
# #             user = User.objects.get(email=email, is_store_owner=True)
# #         except User.DoesNotExist:
# #             messages.error(request, "No store owner found with this email")
# #             return redirect("store_owner_forgot_password")

# #         otp = str(random.randint(100000, 999999))

# #         PasswordResetOTP.objects.create(
# #             user=user,
# #             otp=otp
# #         )

# #         send_otp_email(user.email, otp)

# #         request.session["reset_email"] = email
# #         messages.success(request, "OTP sent to your email")
# #         return redirect("store_owner_verify_otp")

# #     return render(request, "store_owner/forgot_password.html")
# # store_owner/views.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth import get_user_model, login
# from django.utils import timezone
# from accounts.models import PasswordResetOTP
# from accounts.utils import generate_otp, send_otp_email

# User = get_user_model()

# # ----------------------------
# # Forgot Password - Step 1
# # ----------------------------
# def store_owner_forgot_password(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         try:
#             user = User.objects.get(email=email, is_store_owner=True)
#         except User.DoesNotExist:
#             messages.error(request, "No store owner found with this email")
#             return redirect("store_owner_forgot_password")
        
#         # Delete previous OTPs
#         PasswordResetOTP.objects.filter(user=user).delete()
#         otp = generate_otp()
#         PasswordResetOTP.objects.create(user=user, otp=otp)
#         send_otp_email(user.email, otp, purpose="reset")

#         # Save email in session
#         request.session["reset_email"] = email
#         request.session.modified = True

#         messages.success(request, "OTP sent to your email")
#         return redirect("store_owner_forgot_verify_otp")
    
#     return render(request, "store_owner/forgot_password.html")

# # ----------------------------
# # Verify OTP - Step 2
# # ----------------------------
# def store_owner_forgot_verify_otp(request):
#     email = request.session.get("reset_email")
#     if not email:
#         return redirect("store_owner_forgot_password")

#     user = get_object_or_404(User, email=email, is_store_owner=True)

#     if request.method == "POST":
#         otp_input = request.POST.get("otp")
#         try:
#             record = PasswordResetOTP.objects.get(user=user, otp=otp_input)
#         except PasswordResetOTP.DoesNotExist:
#             messages.error(request, "Invalid OTP")
#             return redirect("store_owner_forgot_verify_otp")

#         # Expiry check (10 min)
#         if timezone.now() > record.created_at + timezone.timedelta(minutes=10):
#             record.delete()
#             messages.error(request, "OTP expired")
#             return redirect("store_owner_forgot_password")

#         # OTP correct
#         request.session["reset_user_id"] = user.id
#         request.session["otp_verified"] = True
#         request.session.modified = True

#         record.delete()
#         messages.success(request, "OTP verified! Now reset your password.")
#         return redirect("store_owner_reset_password")

#     return render(request, "store_owner/verify_otp.html")

# # ----------------------------
# # Reset Password - Step 3
# # ----------------------------
# def store_owner_reset_password(request):
#     if not request.session.get("otp_verified"):
#         return redirect("store_owner_forgot_password")

#     user_id = request.session.get("reset_user_id")
#     if not user_id:
#         return redirect("store_owner_forgot_password")

#     user = User.objects.get(id=user_id)

#     if request.method == "POST":
#         password = request.POST.get("password")
#         confirm = request.POST.get("confirm_password")

#         if password != confirm:
#             messages.error(request, "Passwords do not match")
#             return redirect("store_owner_reset_password")

#         user.set_password(password)
#         user.save()

#         # Clear session completely
#         request.session.flush()

#         messages.success(request, "Password reset successful. Please login.")
#         return redirect("store_owner_login")

#     return render(request, "store_owner/reset_password.html")


# from django.utils import timezone
# from accounts.models import PasswordResetOTP

# def store_owner_signup_verify_otp(request):
#     user_id = request.session.get("otp_user_id")
#     if not user_id:
#         return redirect("store_owner_signup")

#     user = CustomUser.objects.get(id=user_id)

#     if request.method == "POST":
#         otp_input = request.POST.get("otp")
#         otp_obj = EmailOTP.objects.filter(user=user).latest("created_at")

#         if otp_obj.is_expired():
#             messages.error(request, "OTP expired")
#             return redirect("store_owner_signup")

#         if otp_input == otp_obj.otp:
#             user.is_active = True
#             user.save()
#             login(request, user)
#             del request.session["otp_user_id"]
#             return redirect("store_owner_dashboard")

#         messages.error(request, "Invalid OTP")

#     return render(request, "store_owner/verify_otp.html")


# # def store_owner_reset_password(request):
# #     if not request.session.get("otp_verified"):
# #         return redirect("store_owner_forgot_password")

# #     user_id = request.session.get("reset_user_id")
# #     user = User.objects.get(id=user_id)

# #     if request.method == "POST":
# #         password = request.POST.get("password")
# #         confirm = request.POST.get("confirm_password")

# #         if password != confirm:
# #             messages.error(request, "Passwords do not match")
# #             return redirect("store_owner_reset_password")

# #         user.set_password(password)
# #         user.save()

# #         request.session.flush()
# #         messages.success(request, "Password reset successful")
# #         return redirect("store_owner_login")

# #     return render(request, "store_owner/reset_password.html")




# def store_owner_logout(request):
#     logout(request)
#     return redirect("store_owner_login")

# # -------- Dashboard --------
# @store_owner_required
# def dashboard(request):
#     stores = Store.objects.filter(owner=request.user)
#     products = Product.objects.filter(store__owner=request.user)
#     return render(request, "store_owner/dashboard.html", {
#         "stores": stores,
#         "products": products
#     })

# # -------- Store CRUD --------
# @store_owner_required
# def add_store(request):
#     form = StoreForm(request.POST or None, request.FILES or None)
#     if form.is_valid():
#         store = form.save(commit=False)
#         store.owner = request.user
#         store.save()
#         messages.success(request, "Store created successfully")
#         return redirect("store_owner_dashboard")
#     return render(request, "store_owner/store_form.html", {"form": form})

# @store_owner_required
# def edit_store(request, id):
#     store = get_object_or_404(Store, id=id, owner=request.user)
#     form = StoreForm(request.POST or None, request.FILES or None, instance=store)
#     if form.is_valid():
#         form.save()
#         messages.success(request, "Store updated successfully")
#         return redirect("store_owner_dashboard")
#     return render(request, "store_owner/store_form.html", {"form": form})

# # -------- Product CRUD --------
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from .forms import ProductForm, ProductStockFormSet, StoreForm
# from accounts.models import Product, Store
# from .decorators import store_owner_required

# # --------------------------
# # Add Product
# # --------------------------
# @store_owner_required
# def add_product(request):
#     form = ProductForm(request.POST or None, request.FILES or None)
#     form.fields['store'].queryset = Store.objects.filter(owner=request.user)
#     stock_formset = ProductStockFormSet(request.POST or None)

#     if form.is_valid() and stock_formset.is_valid():
#         product = form.save(commit=False)
#         # Auto GST from store if empty
#         if not product.gst_number and product.store:
#             product.gst_number = product.store.gst_number
#         product.save()
#         stock_formset.instance = product
#         stock_formset.save()
#         messages.success(request, "Product and stock added successfully")
#         return redirect("store_owner_dashboard")

#     return render(request, "store_owner/product_form.html", {
#         "form": form,
#         "stock_formset": stock_formset
#     })


# # --------------------------
# # Edit Product
# # --------------------------
# @store_owner_required
# def edit_product(request, id):
#     product = get_object_or_404(Product, id=id, store__owner=request.user)

#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES, instance=product)
#         form.fields['store'].queryset = Store.objects.filter(owner=request.user)

#         stock_formset = ProductStockFormSet(
#             request.POST,
#             instance=product   # 🔥 THIS IS MUST
#         )

#         if form.is_valid() and stock_formset.is_valid():
#             form.save()
#             stock_formset.save()
#             messages.success(request, "Product updated successfully")
#             return redirect("store_owner_dashboard")
#         else:
#             print("FORM ERRORS:", form.errors)
#             print("STOCK ERRORS:", stock_formset.errors)

#     else:
#         form = ProductForm(instance=product)
#         form.fields['store'].queryset = Store.objects.filter(owner=request.user)

#         stock_formset = ProductStockFormSet(
#             instance=product   # 🔥 THIS IS MUST
#         )

#     return render(request, "store_owner/product_form.html", {
#         "form": form,
#         "stock_formset": stock_formset
#     })
# @store_owner_required
# def delete_product(request, id):
#     product = get_object_or_404(Product, id=id, store__owner=request.user)
#     product.delete()
#     messages.success(request, "Product deleted successfully")
#     return redirect("store_owner_dashboard")

# # store_owner/views.py

# from accounts.models import OrderItem

# @store_owner_required
# def store_orders(request):
#     orders = OrderItem.objects.select_related("order").filter(
#         product__store__owner=request.user
#     ).order_by("-order__created_at")

#     return render(request, "store_owner/orders.html", {
#         "orders": orders
#     })

# # store_owner/views.py

# from accounts.models import Order

# @store_owner_required
# def mark_packed(request, order_id):
#     order = get_object_or_404(
#         Order,
#         id=order_id,
#         items__product__store__owner=request.user
#     )

#     if order.status != "pending":
#         messages.error(request, "You cannot update this order")
#         return redirect("store_orders")

#     order.status = "packed"
#     order.save()

#     messages.success(request, "Order marked as PACKED")
#     return redirect("store_orders")

# from django.http import JsonResponse
# from accounts.models import OrderItem

# @store_owner_required
# def order_notification_count(request):
#     count = OrderItem.objects.filter(
#         product__store__owner=request.user,
#         order__status="pending"
#     ).count()

#     return JsonResponse({
#         "pending_count": count
#     })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.utils import timezone
from .decorators import store_owner_required
from .forms import StoreForm, ProductForm, ProductStockFormSet,ProductImage
from accounts.models import Store, Product, CustomUser, OrderItem, EmailOTP, PasswordResetOTP
from accounts.utils import generate_otp, send_otp_email
from decimal import Decimal
import random

User = get_user_model()

# ----------------------
# Store Owner Login
# ----------------------
def store_owner_login(request):
    if request.method == "POST":
        user = authenticate(email=request.POST.get("email"), password=request.POST.get("password"))
        if user and user.is_store_owner:
            login(request, user)
            return redirect("store_owner_dashboard")
        messages.error(request, "Invalid credentials")
    return render(request, "store_owner/login.html")


# ----------------------
# Store Owner Signup
# ----------------------
def store_owner_signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")
        
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
            is_active=False   # Important: Activate after OTP verification
        )
        
        otp = generate_otp()
        EmailOTP.objects.create(user=user, otp=otp)
        send_otp_email(email, otp)
        request.session["otp_user_id"] = user.id
        messages.success(request, "OTP sent to your email")
        return redirect("store_owner_verify_otp")
    
    return render(request, "store_owner/signup.html")


# ----------------------
# Signup OTP Verification
# ----------------------
def store_owner_verify_otp(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect("store_owner_signup")
    
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == "POST":
        otp_input = request.POST.get("otp")
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
            
            # Safe deletion of session key
            request.session.pop("otp_user_id", None)
            
            messages.success(request, "Signup successful")
            return redirect("store_owner_dashboard")
        else:
            messages.error(request, "Invalid OTP")
    
    return render(request, "store_owner/verify_otp.html")


# ----------------------
# Forgot Password - Send OTP
# ----------------------
def store_owner_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email, is_store_owner=True)
        except User.DoesNotExist:
            messages.error(request, "No store owner found with this email")
            return redirect("store_owner_forgot_password")
        
        otp = generate_otp()
        PasswordResetOTP.objects.filter(user=user).delete()
        PasswordResetOTP.objects.create(user=user, otp=otp)
        send_otp_email(user.email, otp)
        request.session["reset_email"] = email
        messages.success(request, "OTP sent to your email")
        return redirect("store_owner_forgot_verify_otp")
    
    return render(request, "store_owner/forgot_password.html")


# ----------------------
# Forgot Password - Verify OTP
# ----------------------
def store_owner_forgot_verify_otp(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("store_owner_forgot_password")
    
    user = get_object_or_404(User, email=email, is_store_owner=True)
    
    if request.method == "POST":
        otp_input = request.POST.get("otp")
        try:
            record = PasswordResetOTP.objects.get(user=user, otp=otp_input)
        except PasswordResetOTP.DoesNotExist:
            messages.error(request, "Invalid OTP")
            return redirect("store_owner_forgot_verify_otp")
        
        # Check expiry (5 minutes)
        if timezone.now() > record.created_at + timezone.timedelta(minutes=5):
            record.delete()
            messages.error(request, "OTP expired")
            return redirect("store_owner_forgot_password")
        
        request.session["reset_user_id"] = user.id
        record.delete()
        return redirect("store_owner_reset_password")
    
    return render(request, "store_owner/verify_otp.html")


# ----------------------
# Reset Password
# ----------------------
def store_owner_reset_password(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("store_owner_forgot_password")
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")
        
        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("store_owner_reset_password")
        
        user.set_password(password)
        user.save()
        
        # Clear session safely
        request.session.pop("reset_user_id", None)
        request.session.pop("reset_email", None)
        
        messages.success(request, "Password reset successful")
        return redirect("store_owner_login")
    
    return render(request, "store_owner/reset_password.html")


# ----------------------
# Logout
# ----------------------
def store_owner_logout(request):
    logout(request)
    return redirect("store_owner_login")


# ----------------------
# Dashboard
# ----------------------
@store_owner_required
def dashboard(request):
    stores = Store.objects.filter(owner=request.user)
    products = Product.objects.filter(store__owner=request.user)
    return render(request, "store_owner/dashboard.html", {"stores": stores, "products": products})


# ----------------------
# Store CRUD
# ----------------------
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


# ----------------------
# Product CRUD
# ----------------------
# @store_owner_required
# def add_product(request):
#     form = ProductForm(request.POST or None, request.FILES or None)
#     form.fields['store'].queryset = Store.objects.filter(owner=request.user)
#     stock_formset = ProductStockFormSet(request.POST or None)
    
#     if form.is_valid() and stock_formset.is_valid():
#         product = form.save(commit=False)
#         if not product.gst_number and product.store:
#             product.gst_number = product.store.gst_number
#         product.save()
#         stock_formset.instance = product
#         stock_formset.save()
#         messages.success(request, "Product and stock added successfully")
#         return redirect("store_owner_dashboard")
    
#     return render(request, "store_owner/product_form.html", {"form": form, "stock_formset": stock_formset})

# @store_owner_required
# def add_product(request):
#     form = ProductForm(request.POST or None)
#     form.fields['store'].queryset = Store.objects.filter(owner=request.user)

#     stock_formset = ProductStockFormSet(request.POST or None)
#     image_formset = ProductImageFormSet(
#         request.POST or None,
#         request.FILES or None
#     )

#     if form.is_valid() and stock_formset.is_valid() and image_formset.is_valid():
#         product = form.save(commit=False)
#         if not product.gst_number and product.store:
#             product.gst_number = product.store.gst_number
#         product.save()

#         stock_formset.instance = product
#         stock_formset.save()

#         image_formset.instance = product
#         image_formset.save()

#         messages.success(request, "Product added with multiple images")
#         return redirect("store_owner_dashboard")

#     return render(request, "store_owner/product_form.html", {
#         "form": form,
#         "stock_formset": stock_formset,
#         "image_formset": image_formset
#     })

@store_owner_required
def add_product(request):
    form = ProductForm(request.POST or None)
    form.fields['store'].queryset = Store.objects.filter(owner=request.user)

    stock_formset = ProductStockFormSet(request.POST or None)

    image_formset = ProductImageFormSet(
        request.POST or None,
        request.FILES or None
    )

    if form.is_valid() and stock_formset.is_valid() and image_formset.is_valid():
        product = form.save(commit=False)

        if not product.gst_number and product.store:
            product.gst_number = product.store.gst_number

        product.save()

        stock_formset.instance = product
        stock_formset.save()

        # 🔥 MULTIPLE IMAGE SAVE (CORE LOGIC)
        for form_img in image_formset:
            if form_img.cleaned_data:
                images = request.FILES.getlist(
                    f"{form_img.prefix}-image"
                )
                for img in images:
                    ProductImage.objects.create(
                        product=product,
                        image=img
                    )

        messages.success(request, "Product added with multiple images")
        return redirect("store_owner_dashboard")

    return render(request, "store_owner/product_form.html", {
        "form": form,
        "stock_formset": stock_formset,
        "image_formset": image_formset
    })

# @store_owner_required
# def edit_product(request, id):
#     product = get_object_or_404(Product, id=id, store__owner=request.user)
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES, instance=product)
#         form.fields['store'].queryset = Store.objects.filter(owner=request.user)
#         stock_formset = ProductStockFormSet(request.POST, instance=product)
#         if form.is_valid() and stock_formset.is_valid():
#             form.save()
#             stock_formset.save()
#             messages.success(request, "Product updated successfully")
#             return redirect("store_owner_dashboard")
#     else:
#         form = ProductForm(instance=product)
#         form.fields['store'].queryset = Store.objects.filter(owner=request.user)
#         stock_formset = ProductStockFormSet(instance=product)
    
#     return render(request, "store_owner/product_form.html", {"form": form, "stock_formset": stock_formset})
from .forms import StoreForm, ProductForm, ProductStockFormSet,  ProductImageFormSet
@store_owner_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id, store__owner=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        form.fields['store'].queryset = Store.objects.filter(owner=request.user)

        stock_formset = ProductStockFormSet(request.POST, instance=product)
        image_formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid() and stock_formset.is_valid() and image_formset.is_valid():
            form.save()
            stock_formset.save()
            image_formset.save()
            messages.success(request, "Product updated successfully")
            return redirect("store_owner_dashboard")
    else:
        form = ProductForm(instance=product)
        form.fields['store'].queryset = Store.objects.filter(owner=request.user)

        stock_formset = ProductStockFormSet(instance=product)
        image_formset = ProductImageFormSet(instance=product)

    return render(request, "store_owner/product_form.html", {
        "form": form,
        "stock_formset": stock_formset,
        "image_formset": image_formset
    })

@store_owner_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id, store__owner=request.user)
    product.delete()
    messages.success(request, "Product deleted successfully")
    return redirect("store_owner_dashboard")


# ----------------------
# Orders
# ----------------------
@store_owner_required
def store_orders(request):
    orders = OrderItem.objects.select_related("order").filter(product__store__owner=request.user).order_by("-order__created_at")
    return render(request, "store_owner/orders.html", {"orders": orders})


@store_owner_required
def mark_packed(request, order_id):
    from accounts.models import Order
    order = get_object_or_404(Order, id=order_id, items__product__store__owner=request.user)
    if order.status != "pending":
        messages.error(request, "You cannot update this order")
    else:
        order.status = "packed"
        order.save()
        messages.success(request, "Order marked as PACKED")
    return redirect("store_orders")


@store_owner_required
def order_notification_count(request):
    count = OrderItem.objects.filter(product__store__owner=request.user, order__status="pending").count()
    from django.http import JsonResponse
    return JsonResponse({"pending_count": count})