from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .utils import send_otp_email
import random
from .models import ProductStock,UserAddress

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


# @login_required
# def cart(request):
#     cart = request.session.get('cart', {})
#     cart_items = []
#     for key, qty in cart.items():
#         product_id, size = key.split('_')
#         product = Product.objects.get(id=product_id)
#         cart_items.append({
#             'product': product,
#             'size': size,
#             'quantity': qty,
#         })
#     return render(request, 'cart.html', {'cart_items': cart_items})


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
from .models import Store, Product, StoreCategory
import random
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from collections import defaultdict
import random
from .models import Store, StoreCategory, Product

@login_required
def home(request):
    user = request.user

    # ================= GET PARAMETERS =================
    selected_category = request.GET.get('category')
    product_q = request.GET.get('product_q', '')
    store_q = request.GET.get('store_q', '')

    # ================= STORES (Location + Category + Store Search) =================
    stores = Store.objects.filter(
        country=user.country,
        state=user.state,
        district=user.district,
        block=user.block,
        is_active=True
    )

    if selected_category and selected_category.isdigit():
        stores = stores.filter(category__id=int(selected_category))

    if store_q:
        stores = stores.filter(name__icontains=store_q)

    # ================= STORE CATEGORIES (ICON + NAME) =================
    store_categories = StoreCategory.objects.filter(
        stores__country=user.country,
        stores__state=user.state,
        stores__district=user.district,
        stores__block=user.block,
        stores__is_active=True
    ).distinct()

    # ================= PRODUCTS (Availability + Product Search) =================
    products = Product.objects.filter(is_available=True)

    if product_q:
        products = products.filter(name__icontains=product_q)

    # organize products by category
    products_by_category = defaultdict(list)
    for p in products:
        cat_name = p.category.name if p.category else 'Uncategorized'
        products_by_category[cat_name].append(p)

    # Shuffle products inside each category
    for plist in products_by_category.values():
        random.shuffle(plist)

    context = {
        'stores': stores,
        'store_categories': store_categories,
        'selected_category': selected_category,
        'products_by_category': dict(products_by_category),
        'product_q': product_q,
        'store_q': store_q,
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

from django.shortcuts import render, get_object_or_404
from collections import defaultdict
from django.db.models import Q
from .models import Store, Product

# def store_detail(request, id):
#     store = get_object_or_404(Store, id=id, is_active=True)
#     products = store.products.filter(is_available=True)

#     # ---------------- SEARCH QUERY ----------------
#     query = request.GET.get('q')
#     if query:
#         products = products.filter(
#             Q(name__icontains=query) | Q(description__icontains=query)
#         )

#     # ---------------- GROUP BY CATEGORY ----------------
#     products_by_category = defaultdict(list)
#     for product in products:
#         category_name = product.category.name if product.category else 'Uncategorized'
#         # Calculate discount percentage
#         if product.discounted_price and product.discounted_price < product.price:
#             product.discount_percentage = round((product.price - product.discounted_price) / product.price * 100)
#         else:
#             product.discount_percentage = 0
#         products_by_category[category_name].append(product)

#     context = {
#         'store': store,
#         'products_by_category': dict(products_by_category),
#         'search_query': query or '',  # template re show search term
#     }
#     return render(request, 'store_detail.html', context)
from django.http import JsonResponse
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Store, Product

def store_detail(request, id):
    store = get_object_or_404(Store, id=id, is_active=True)
    products = store.products.filter(is_available=True)

    query = request.GET.get('q', '').strip()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        # Return JSON for AJAX live search
        products_data = []
        for product in products:
            discount = round((product.price - product.discounted_price) / product.price * 100) if product.discounted_price else 0
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'discounted_price': product.discounted_price,
                'discount_percentage': discount,
                'image': product.image.url if product.image else '/static/default_product.jpg'
            })
        return JsonResponse({'products': products_data})

    # Group products by category for normal page render
    products_by_category = defaultdict(list)
    for product in products:
        category_name = product.category.name if product.category else 'Uncategorized'
        if product.discounted_price and product.discounted_price < product.price:
            product.discount_percentage = round((product.price - product.discounted_price) / product.price * 100)
        else:
            product.discount_percentage = 0
        products_by_category[category_name].append(product)

    return render(request, 'store_detail.html', {
        'store': store,
        'products_by_category': dict(products_by_category),
        'search_query': query,
    })

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
# from django.shortcuts import redirect, get_object_or_404
# from .models import Product, ProductStock

# def add_to_cart(request, product_id, size):
#     product = get_object_or_404(Product, id=product_id)
#     # Example: simple cart in session
#     cart = request.session.get('cart', {})
#     key = f"{product_id}_{size}"
#     if key in cart:
#         cart[key] += 1
#     else:
#         cart[key] = 1
#     request.session['cart'] = cart
#     request.session.modified = True
#     return redirect('cart')


# # accounts/views.py
# from django.shortcuts import redirect, get_object_or_404
# from .models import Product, ProductStock

# def buy_now(request, product_id, size):
#     # Example: redirect to cart page with single item
#     product = get_object_or_404(Product, id=product_id)
#     cart = request.session.get('cart', {})
#     key = f"{product_id}_{size}"
#     cart[key] = 1  # set quantity 1 for buy now
#     request.session['cart'] = cart
#     request.session.modified = True
#     return redirect('cart')  # or redirect to checkout page if exists
# def add_to_cart(request, product_id, size):
#     product = get_object_or_404(Product, id=product_id)
#     cart = request.session.get('cart', {})
#     key = f"{product_id}_{size}"
#     cart[key] = cart.get(key, 0) + 1
#     request.session['cart'] = cart
#     request.session.modified = True
#     return redirect('cart')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product

from django.contrib import messages
from django.shortcuts import redirect

def add_to_cart(request, product_id, size):
    cart = request.session.get("cart", {})
    key = f"{product_id}_{size}"   # product_id + size

    # ❌ already exists → do NOT increase quantity
    if key in cart:
        messages.warning(
            request,
            "This product with selected size is already in your cart"
        )
        return redirect("cart")

    # ✅ first time add only
    cart[key] = 1

    request.session["cart"] = cart
    request.session.modified = True

    messages.success(request, "Product added to cart")
    return redirect("cart")

@login_required
def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0   # ✅ name match with template

    for key, qty in cart.items():
        try:
            product_id, size = key.split('_')
            product = get_object_or_404(Product, id=product_id)
            stock = ProductStock.objects.get(product=product, size=size)

            # ✅ price choose (discount > normal)
            price = product.discounted_price if product.discounted_price else product.price

            item_total = price * qty
            cart_total += item_total

            cart_items.append({
                'product': product,
                'size': size,
                'quantity': qty,
                'stock': stock.stock,
                'price': price,
                'item_total': item_total,
            })

        except ProductStock.DoesNotExist:
            continue

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total   # ✅ THIS FIXES MOBILE + DESKTOP
    })
@login_required
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty")
        return redirect('cart')

    # 🔥 future re eithi Order model save kariba
    # for now only success message

    request.session['cart'] = {}
    request.session.modified = True

    messages.success(request, "Order placed successfully 🎉")
    return redirect('home')

# def buy_now(request, product_id, size):
#     product = get_object_or_404(Product, id=product_id)
#     cart = {f"{product_id}_{size}": 1}
#     request.session['cart'] = cart
#     request.session.modified = True
#     return redirect('cart')  # or checkout page

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
    
@login_required
def remove_from_cart(request, product_id, size):
    cart = request.session.get('cart', {})
    key = f"{product_id}_{size}"
    if key in cart:
        del cart[key]
        request.session.modified = True
    return redirect('cart')

@login_required
def update_cart_quantity(request, product_id, size):
    if request.method == 'POST':
        qty = int(request.POST.get('qty',1))
        cart = request.session.get('cart',{})
        key = f"{product_id}_{size}"
        if key in cart:
            cart[key] = qty
            request.session['cart'] = cart
            request.session.modified = True
    return redirect('cart')    

@login_required
def increase_qty(request, product_id, size):
    cart = request.session.get('cart', {})
    key = f"{product_id}_{size}"

    try:
        stock_obj = ProductStock.objects.get(product_id=product_id, size=size)
        max_stock = stock_obj.stock
    except ProductStock.DoesNotExist:
        max_stock = 0

    if key in cart:
        if cart[key] < max_stock:
            cart[key] += 1
    else:
        if max_stock > 0:
            cart[key] = 1

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')


@login_required
def decrease_qty(request, product_id, size):
    cart = request.session.get('cart', {})
    key = f"{product_id}_{size}"

    if key in cart:
        if cart[key] > 1:
            cart[key] -= 1
        else:
            del cart[key]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')

from django.http import JsonResponse
from django.db.models import Q

def live_search(request):
    q = request.GET.get("q", "").strip()

    products = Product.objects.filter(
        Q(name__icontains=q),
        is_available=True
    )[:5]

    stores = Store.objects.filter(
        Q(name__icontains=q),
        is_active=True
    )[:5]

    data = {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "price": p.discounted_price if p.discounted_price else p.price,
                "image": p.image.url if p.image else ""
            } for p in products
        ],
        "stores": [
            {
                "id": s.id,
                "name": s.name,
                "image": s.image.url if s.image else ""
            } for s in stores
        ]
    }
    return JsonResponse(data)


def buy_now(request, product_id, size):
    request.session['buy_now'] = {
        'product_id': product_id,
        'size': size,
        'qty': 1
    }
    request.session['checkout_type'] = 'buy_now'
    return redirect('checkout_address')

@login_required
def checkout_address(request):
    if request.GET.get('from') == 'cart':
        request.session['checkout_type'] = 'cart'
        request.session.pop('buy_now', None)  # ✅ only here clear

    addresses = UserAddress.objects.filter(user=request.user)
    return render(request, 'checkout/address.html', {
        'addresses': addresses
    })

# ---------------------------
# Save New Address View
# ---------------------------
@login_required
def save_address(request):
    if request.method == 'POST':
        is_default = not UserAddress.objects.filter(user=request.user).exists()

        UserAddress.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            mobile=request.POST.get('mobile'),
            alt_mobile=request.POST.get('alt_mobile'),
            pincode=request.POST.get('pincode'),
            address=request.POST.get('address'),
            is_default=is_default
        )

        # 🔥 checkout_type jodi already achhi tahale overwrite karibani
        if 'checkout_type' not in request.session:
            request.session['checkout_type'] = 'cart'

        return redirect('checkout_summary')

    return redirect('checkout_address')   
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
@login_required
def checkout_summary(request):
    checkout_type = request.session.get('checkout_type', 'cart')

    # 📍 Default address
    address = UserAddress.objects.filter(
        user=request.user,
        is_default=True
    ).first()

    if not address:
        messages.info(request, "Please add delivery address")
        return redirect('checkout_address')

    items = []
    total_amount = 0
    original_total = 0

    # ==========================
    # ⚡ BUY NOW FLOW
    # ==========================
    if checkout_type == 'buy_now' and request.session.get('buy_now'):
        buy = request.session['buy_now']
        product = get_object_or_404(Product, id=buy['product_id'])

        price = product.discounted_price or product.price
        qty = buy.get('qty', 1)

        item_total = price * qty
        total_amount = item_total
        original_total = product.price * qty

        items.append({
            'product': product,
            'size': buy['size'],
            'qty': qty,
            'price': price,
            'item_total': item_total
        })

    # ==========================
    # 🛒 CART FLOW
    # ==========================
    else:
        cart = request.session.get('cart')
        if not cart:
            messages.warning(request, "Your cart is empty")
            return redirect('cart')

        for key, qty in cart.items():
            try:
                product_id, size = key.split('_')
            except ValueError:
                continue

            product = get_object_or_404(Product, id=product_id)
            price = product.discounted_price or product.price

            item_total = price * qty
            original_total += product.price * qty
            total_amount += item_total

            items.append({
                'product': product,
                'size': size,
                'qty': qty,
                'price': price,
                'item_total': item_total
            })

    discount = original_total - total_amount

    # 🔥 Payment pain session save
    request.session['order_total'] = float(total_amount)
    request.session['order_discount'] = float(discount)
    request.session['order_items_count'] = len(items)

    return render(request, 'checkout/summary.html', {
        'address': address,
        'items': items,
        'original_price': original_total,
        'discount': discount,
        'total_amount': total_amount
    })

@login_required
def checkout_payment(request):
    return render(request, 'checkout/payment.html')



def change_address(request):
    # later: fetch saved addresses from DB
    return render(request, 'checkout/change_address.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import UserAddress  # jaha address model achhi
from django.contrib.auth.decorators import login_required

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        address.name = request.POST.get('name')
        address.mobile = request.POST.get('mobile')
        address.alt_mobile = request.POST.get('alt_mobile')
        address.pincode = request.POST.get('pincode')
        address.address = request.POST.get('address')
        address.save()
        return redirect('checkout_summary')

    return render(request, 'checkout/edit_address.html', {'address': address})