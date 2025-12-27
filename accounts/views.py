from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .utils import send_otp_email
import random

from .forms import ProfileForm

User = get_user_model()



# ======================
# AUTH – SIGNUP WITH OTP
# ======================
def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm_password']

        if password != confirm:
            return render(request, 'signup.html', {'error': "Passwords do not match"})

        if User.objects.filter(email=email, is_verified=True).exists():
            return render(request, 'signup.html', {'error': "Email already registered"})

        otp = random.randint(100000, 999999)

        request.session['signup_data'] = {
            'email': email,
            'password': password,
            'otp': str(otp)
        }

        send_otp_email(email, otp)   # ✅ FIXED

        return redirect('verify_otp')

    return render(request, 'signup.html')


def verify_otp(request):
    data = request.session.get('signup_data')
    if not data:
        return redirect('signup')

    if request.method == 'POST':
        if request.POST['otp'] == data['otp']:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={'is_verified': True}
            )
            if created:
                user.set_password(data['password'])
                user.save()

            del request.session['signup_data']
            login(request, user)
            return redirect('home')

        return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_otp.html')


# =========
# LOGIN
# =========

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return redirect('home')

        return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# =================
# FORGOT PASSWORD
# =================

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            return render(request, 'forgot_password.html', {'error': 'Email not found'})

        otp = random.randint(100000, 999999)

        request.session['reset_otp'] = {
            'email': email,
            'otp': str(otp)
        }

        send_otp_email(email, otp)   # ✅ FIXED

        return redirect('verify_reset_otp')

    return render(request, 'forgot_password.html')


def verify_reset_otp(request):
    data = request.session.get('reset_otp')
    if not data:
        return redirect('forgot_password')

    if request.method == 'POST':
        if request.POST['otp'] == data['otp']:
            request.session['reset_email'] = data['email']
            request.session.pop('reset_otp')
            return redirect('reset_password')

        return render(request, 'verify_reset_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_reset_otp.html')


def reset_password(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST['password']
        confirm = request.POST['confirm_password']

        if password != confirm:
            return render(request, 'reset_password.html', {'error': 'Passwords do not match'})

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        request.session.pop('reset_email')

        return redirect('login')

    return render(request, 'reset_password.html')


# =====================
# APP PAGES (NAVBAR)
# =====================

@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def cart(request):
    return render(request, 'cart.html')


@login_required
def cart_history(request):
    return render(request, 'cart_history.html')


@login_required
def location(request):
    return render(request, 'location.html')


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'profile.html', {'form': form})

from .models import Store

# accounts/views.py
from .models import Store

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Store, Product
import random

# @login_required
# def home(request):
#     user = request.user

#     # Filter stores based on user location
#     stores = Store.objects.filter(
#         country=user.country,
#         state=user.state,
#         district=user.district,
#         block=user.block
#     )

#     # Get all products and shuffle them randomly
#     products = list(Product.objects.all())
#     random.shuffle(products)

#     context = {
#         'stores': stores,
#         'products': products,  # pass products to template
#     }

#     return render(request, 'home.html', context)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from .models import Store, Product
import random

@login_required
def home(request):
    user = request.user

    # Filter stores by user location
    stores = Store.objects.filter(
        country=user.country,
        state=user.state,
        district=user.district,
        block=user.block
    )

    # Products grouped by category
    products = Product.objects.all()
    products_by_category = defaultdict(list)
    for p in products:
        cat_name = p.category.name if p.category else 'Uncategorized'
        products_by_category[cat_name].append(p)

    # Shuffle products in each category
    for plist in products_by_category.values():
        random.shuffle(plist)

    context = {
        'stores': stores,
        'products_by_category': dict(products_by_category)
    }

    return render(request, 'home.html', context)

from django.http import HttpResponse
from .models import State, District, Block

def load_states(request):
    country_id = request.GET.get('country')
    states = State.objects.filter(country_id=country_id).order_by('name')
    return HttpResponse('\n'.join([f'<option value="{s.id}">{s.name}</option>' for s in states]))

def load_districts(request):
    state_id = request.GET.get('state')
    districts = District.objects.filter(state_id=state_id).order_by('name')
    return HttpResponse('\n'.join([f'<option value="{d.id}">{d.name}</option>' for d in districts]))

def load_blocks(request):
    district_id = request.GET.get('district')
    blocks = Block.objects.filter(district_id=district_id).order_by('name')
    return HttpResponse('\n'.join([f'<option value="{b.id}">{b.name}</option>' for b in blocks]))
from collections import defaultdict

from collections import defaultdict

def store_detail(request, id):
    store = get_object_or_404(Store, id=id, is_active=True)
    products = store.products.filter(is_available=True)
    
    # Group products by category name; if category is None, group as 'Uncategorized'
    products_by_category = defaultdict(list)
    for product in products:
        category_name = product.category.name if product.category else 'Uncategorized'
        products_by_category[category_name].append(product)
    
    context = {
        'store': store,
        'products_by_category': dict(products_by_category)
    }
    return render(request, 'store_detail.html', context)

# from django.shortcuts import render, get_object_or_404
# from django.db.models import Q
# from .models import Product

# def product_detail(request, id):
#     product = get_object_or_404(Product, id=id)

#     # 1️⃣ Same store + same category (first priority)
#     similar_products = Product.objects.filter(
#         store=product.store,
#         category=product.category
#     ).exclude(id=product.id)

#     # 2️⃣ If not enough → same store random products
#     if similar_products.count() < 4:
#         same_store_random = Product.objects.filter(
#             store=product.store
#         ).exclude(id=product.id)

#         similar_products = (similar_products | same_store_random).distinct()

#     # 3️⃣ If still not enough → other store random products
#     if similar_products.count() < 4:
#         other_store_random = Product.objects.exclude(
#             Q(store=product.store) | Q(id=product.id)
#         ).order_by('?')[:4]

#         similar_products = (similar_products | other_store_random).distinct()

#     context = {
#         "product": product,
#         "similar_products": similar_products[:4]  # show only 4
#     }

#     return render(request, 'product_detail.html', context)
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product
import random

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    # Step 1: same store + same category
    similar_products = list(Product.objects.filter(
        store=product.store,
        category=product.category
    ).exclude(id=product.id))

    # Step 2: if not enough, add same store random products
    if len(similar_products) < 4:
        same_store_random = list(Product.objects.filter(
            store=product.store
        ).exclude(id=product.id))
        for p in same_store_random:
            if p not in similar_products:
                similar_products.append(p)

    # Step 3: if still not enough, add other store random products
    if len(similar_products) < 4:
        other_store_random = list(Product.objects.exclude(
            Q(store=product.store) | Q(id=product.id)
        ))
        for p in other_store_random:
            if p not in similar_products:
                similar_products.append(p)

    # Step 4: shuffle and limit to 4
    random.shuffle(similar_products)
    similar_products = similar_products[:4]

    context = {
        "product": product,
        "similar_products": similar_products
    }
    return render(request, 'product_detail.html', context)

# accounts/views.py
from django.shortcuts import redirect, get_object_or_404
from .models import Product, ProductStock

def add_to_cart(request, product_id, size):
    product = get_object_or_404(Product, id=product_id)
    # Example: simple cart in session
    cart = request.session.get('cart', {})
    key = f"{product_id}_{size}"
    if key in cart:
        cart[key] += 1
    else:
        cart[key] = 1
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')


# accounts/views.py
from django.shortcuts import redirect, get_object_or_404
from .models import Product, ProductStock

def buy_now(request, product_id, size):
    # Example: redirect to cart page with single item
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    key = f"{product_id}_{size}"
    cart[key] = 1  # set quantity 1 for buy now
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')  # or redirect to checkout page if exists

from django.http import HttpResponse
from django.contrib.auth import get_user_model

def create_superuser(request):
    User = get_user_model()
    email = "admin@gmail.com"
    password = "Admin@123"
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return HttpResponse("Password updated for existing superuser.")
    else:
        User.objects.create_superuser(email=email, password=password)
        return HttpResponse("Superuser created successfully.")