from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .utils import send_otp_email
import random
from .models import ProductStock,UserAddress,Order, OrderItem

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
def cart_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cart_history.html', {'orders': orders})


@login_required
def location(request):
    return render(request, 'location.html')



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm

@login_required
def profile(request):
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()   # ✅ ONE TIME SAVE
            return redirect("home")
    else:
        form = ProfileForm(instance=user)

    return render(request, "profile.html", {"form": form})
from .models import Store

# accounts/views.py
from .models import Store

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Store, Product
import random


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

from collections import defaultdict
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home(request):
    user = request.user

    # ================= GET PARAMETERS =================
    selected_category = request.GET.get('category')
    product_q = request.GET.get('product_q', '')
    store_q = request.GET.get('store_q', '')

    # ================= STORES (LOCATION PRIORITY) =================
    stores = Store.objects.filter(is_active=True)

    if user.village:
        stores = stores.filter(village=user.village)
    elif user.block:
        stores = stores.filter(block=user.block)
    elif user.district:
        stores = stores.filter(district=user.district)
    elif user.state:
        stores = stores.filter(state=user.state)
    elif user.country:
        stores = stores.filter(country=user.country)

    # ================= STORE CATEGORY FILTER =================
    if selected_category and selected_category.isdigit():
        stores = stores.filter(category__id=int(selected_category))

    # ================= STORE SEARCH =================
    if store_q:
        stores = stores.filter(name__icontains=store_q)

    # ================= STORE CATEGORIES (FOR TOP BAR) =================
    store_categories = StoreCategory.objects.all()

    # ================= PRODUCTS (MAIN FIX) =================
    products = Product.objects.filter(
        is_available=True,
        store__in=stores   # 🔥 IMPORTANT LINE
    )

    if product_q:
        products = products.filter(
            Q(name__icontains=product_q) |
            Q(category__name__icontains=product_q)
    )

    # ================= PRODUCTS BY PRODUCT CATEGORY =================
    products_by_category = defaultdict(list)

    for p in products.select_related('category'):
        cat_name = p.category.name if p.category else 'Uncategorized'
        if len(products_by_category[cat_name]) < 6:
            products_by_category[cat_name].append(p)

    # shuffle each category products
    for plist in products_by_category.values():
        random.shuffle(plist)

    # ================= CONTEXT =================
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


from django.http import JsonResponse
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Store, Product
# def store_detail(request, id):
#     store = get_object_or_404(Store, id=id, is_active=True)
#     products = store.products.filter(is_available=True)

#     query = request.GET.get('q', '').strip()
#     if query:
#         products = products.filter(
#             Q(name__icontains=query) | Q(description__icontains=query)
#         )

#     products_by_category = defaultdict(list)

#     for product in products:
#         category_name = product.category.name if product.category else 'Uncategorized'

#         if product.discounted_price and product.discounted_price < product.price:
#             product.discount_percentage = round(
#                 (product.price - product.discounted_price) / product.price * 100
#             )
#         else:
#             product.discount_percentage = 0

#         products_by_category[category_name].append(product)

#     # 🔥 LIMIT 6 PER CATEGORY
#     for cat in products_by_category:
#         random.shuffle(products_by_category[cat])
#         products_by_category[cat] = products_by_category[cat][:6]

#     return render(request, 'store_detail.html', {
#         'store': store,
#         'products_by_category': dict(products_by_category),
#         'search_query': query,
#     })
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from collections import defaultdict
import random
from .models import Store, Product

def store_detail(request, id):
    store = get_object_or_404(Store, id=id, is_active=True)
    products = store.products.filter(is_available=True)
    query = request.GET.get('q', '').strip()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # ===== AJAX REQUEST =====
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for p in products:
            if p.image:
                img_url = p.image.url
            elif p.images.exists():
                img_url = p.images.first().image.url
            else:
                img_url = ""  # Or default image url

            data.append({
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "discounted_price": float(p.discounted_price) if p.discounted_price else None,
                "discount_percentage": round((p.price - p.discounted_price) / p.price * 100) if p.discounted_price else 0,
                "image": img_url,
                "category": p.category.name if p.category else "Uncategorized",
            })
        return JsonResponse({"products": data})

    # ===== NORMAL PAGE LOAD =====
    products_by_category = defaultdict(list)
    for product in products:
        cat_name = product.category.name if product.category else "Uncategorized"
        product.discount_percentage = round((product.price - product.discounted_price) / product.price * 100) if product.discounted_price else 0
        products_by_category[cat_name].append(product)

    for cat in products_by_category:
        random.shuffle(products_by_category[cat])
        products_by_category[cat] = products_by_category[cat][:6]

    return render(request, "store_detail.html", {
        "store": store,
        "products_by_category": dict(products_by_category),
        "search_query": query,
    })


from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product
import random

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from collections import defaultdict
from .models import Product, ProductStock
from collections import defaultdict
from django.shortcuts import get_object_or_404, render




from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product
import random


from .models import ProductStock


from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from collections import defaultdict
from .models import Product, ProductStock
from collections import defaultdict
from django.shortcuts import get_object_or_404, render

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    viewed = request.session.get("recently_viewed", [])

    if product.id not in viewed:
        viewed.insert(0, product.id)

    request.session["recently_viewed"] = viewed[:10]  # max 10 
    # =========================
    # AVAILABLE SIZES (stock > 0)
    # =========================
    available_stocks = ProductStock.objects.filter(
        product=product,
        stock__gt=0
    )
    
    # =========================
    # SIMILAR PRODUCTS (CATEGORY WISE)
    # =========================
    products = Product.objects.filter(
        is_available=True
    ).exclude(id=product.id).select_related('category')
    
    products_by_category = defaultdict(list)
    for p in products:
        if p.category:   # safety
            # Calculate % OFF for each similar product
            if p.discounted_price and p.price > 0:
                p.off_percent = int(((p.price - p.discounted_price) / p.price) * 100)
            else:
                p.off_percent = 0
            products_by_category[p.category].append(p)
    
    # Optional: limit per category (performance + UI)
    for cat in products_by_category:
        products_by_category[cat] = products_by_category[cat][:10]

    # =========================
    # CALCULATE % OFF FOR MAIN PRODUCT
    # =========================
    if product.discounted_price and product.price > 0:
        product.off_percent = int(((product.price - product.discounted_price) / product.price) * 100)
    else:
        product.off_percent = 0

    context = {
        "product": product,
        "available_stocks": available_stocks,
        "products_by_category": dict(products_by_category),
    }
    
    return render(request, "product_detail.html", context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product

from django.contrib import messages
from django.shortcuts import redirect


def add_to_cart(request, product_id, size):
    product = get_object_or_404(Product, id=product_id)

    try:
        stock = ProductStock.objects.get(product=product, size=size)
    except ProductStock.DoesNotExist:
        messages.error(request, "Invalid size selected")
        return redirect("product_detail", id=product_id)

    # ❌ OUT OF STOCK
    if stock.stock <= 0:
        messages.error(request, "Selected size is out of stock")
        return redirect("product_detail", id=product_id)

    cart = request.session.get("cart", {})
    key = f"{product_id}_{size}"

    if key in cart:
        messages.warning(
            request,
            "This product with selected size is already in your cart"
        )
        return redirect("cart")

    cart[key] = 1
    request.session["cart"] = cart
    request.session.modified = True

    messages.success(request, "Product added to cart")
    return redirect("cart")

@login_required
def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0
    cart_subtotal = 0
    product_ids_in_cart = []

    for key, qty in cart.items():
        try:
            product_id, size = key.split('_')
            product = get_object_or_404(Product, id=product_id)
            stock = ProductStock.objects.get(product=product, size=size)

            price = product.discounted_price or product.price
            item_total = price * qty

            cart_total += item_total
            cart_subtotal += product.price * qty

            off_percent = 0
            if product.discounted_price:
                off_percent = round(
                    (product.price - product.discounted_price) / product.price * 100
                )

            cart_items.append({
                'product': product,
                'size': size,
                'quantity': qty,
                'stock': stock.stock,
                'price': price,
                'item_total': item_total,
                'off_percent': off_percent,
            })

            product_ids_in_cart.append(product.id)

        except ProductStock.DoesNotExist:
            continue

    # =========================
    # 🔥 RELATED / EMPTY CART PRODUCTS
    # =========================
    related_products = []
    empty_cart_products = []

    # 🟢 Cart has items → related products
    if cart_items:
        first_product = cart_items[0]['product']

        qs = Product.objects.filter(
            Q(category=first_product.category) |
            Q(name__icontains=first_product.name.split()[0])
        ).exclude(id__in=product_ids_in_cart)

        related_products = list(qs)

        if len(related_products) < 6:
            extra = list(
                Product.objects.exclude(id__in=product_ids_in_cart)
                .exclude(id__in=[p.id for p in related_products])
            )
            related_products += extra

        random.shuffle(related_products)
        related_products = related_products[:6]

    # 🔴 Cart empty → recently viewed / random
    else:
        viewed_ids = request.session.get("recently_viewed", [])

        if viewed_ids:
            empty_cart_products = list(
                Product.objects.filter(id__in=viewed_ids, is_available=True)[:6]
            )

        if not empty_cart_products:
            empty_cart_products = list(
                Product.objects.filter(is_available=True).order_by("?")[:6]
            )

    context = {
        "cart_items": cart_items,
        "cart_total": cart_total,
        "cart_subtotal": cart_subtotal,
        "related_products": related_products,
        "empty_cart_products": empty_cart_products,
    }

    return render(request, "cart.html", context)

from django.db import transaction
from .models import ProductStock



from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
@transaction.atomic
def place_order(request):
    if request.method != 'POST':
        return redirect('checkout_payment')

    payment_method = request.POST.get('payment_method')
    checkout_type = request.session.get('checkout_type', 'cart')

    address = UserAddress.objects.filter(
        user=request.user,
        is_default=True
    ).first()

    if not address:
        messages.error(request, "Please add delivery address")
        return redirect('checkout_address')

    items = []
    subtotal = 0
    delivery_total = 0   # ✅ IMPORTANT

    # ================= BUY NOW =================
    if checkout_type == 'buy_now' and request.session.get('buy_now'):
        buy = request.session['buy_now']
        product = get_object_or_404(Product, id=buy['product_id'])
        size = buy['size']
        qty = buy.get('qty', 1)

        price = product.discounted_price or product.price
        delivery_charge = product.delivery_charge or 0

        stock = ProductStock.objects.select_for_update().get(
            product=product,
            size=size
        )
        if stock.stock < qty:
            messages.error(request, "Product out of stock")
            return redirect('cart')

        stock.stock -= qty
        stock.save()

        subtotal += price * qty
        delivery_total += delivery_charge * qty   # ✅ per product

        items.append({
            'product': product,
            'size': size,
            'price': price,
            'qty': qty
        })

    # ================= CART =================
    else:
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Cart empty")
            return redirect('cart')

        for key, qty in cart.items():
            product_id, size = key.split('_')
            product = get_object_or_404(Product, id=product_id)

            price = product.discounted_price or product.price
            delivery_charge = product.delivery_charge or 0

            stock = ProductStock.objects.select_for_update().get(
                product=product,
                size=size
            )
            if stock.stock < qty:
                messages.error(request, f"{product.name} ({size}) out of stock")
                return redirect('cart')

            stock.stock -= qty
            stock.save()

            subtotal += price * qty
            delivery_total += delivery_charge * qty   # ✅ per product

            items.append({
                'product': product,
                'size': size,
                'price': price,
                'qty': qty
            })

    # ================= ORDER CREATE =================
    total_amount = subtotal + delivery_total

    order = Order.objects.create(
        user=request.user,
        subtotal=subtotal,
        shipping_cost=delivery_total,      # ✅ REAL delivery
        total_amount=total_amount,          # ✅ FINAL amount
        payment_method=payment_method,
        delivery_name=address.name,
        delivery_phone=address.mobile,
        delivery_address=address.address,
        delivery_city=f"{address.block}, {address.district}, {address.state}",
        delivery_postal_code=address.pincode
    )

    # ================= ORDER ITEMS =================
    for i in items:
        OrderItem.objects.create(
            order=order,
            product=i['product'],
            product_name=i['product'].name,
            size=i['size'],
            price=i['price'],
            quantity=i['qty'],
            gst_rate=i['product'].gst_rate,      # add GST rate
            gst_number=i['product'].gst_number   # add GST number
        )

    # ================= CLEAN SESSION =================
    request.session.pop('cart', None)
    request.session.pop('buy_now', None)
    request.session.pop('checkout_type', None)

    messages.success(request, "Order placed successfully 🎉")
    return redirect('cart_history')

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
    product = get_object_or_404(Product, id=product_id)

    try:
        stock = ProductStock.objects.get(product=product, size=size)
    except ProductStock.DoesNotExist:
        messages.error(request, "Invalid size")
        return redirect("product_detail", id=product_id)

    if stock.stock <= 0:
        messages.error(request, "Selected size is out of stock")
        return redirect("product_detail", id=product_id)

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
        request.session.pop('buy_now', None)

    # ✅ check default address
    default_address = UserAddress.objects.filter(
        user=request.user,
        is_default=True
    ).first()

    # 🔥 IF address already exists → skip address page
    if default_address:
        return redirect('checkout_summary')

    # ❌ No address yet → show address form
    return render(request, 'checkout/address.html')


# @login_required
# def save_address(request):
#     if request.method == 'POST':

#         # 🔴 Make all old addresses non-default
#         UserAddress.objects.filter(
#             user=request.user,
#             is_default=True
#         ).update(is_default=False)

#         # ✅ Save new address as default
#         UserAddress.objects.create(
#             user=request.user,
#             name=request.POST.get('name'),
#             mobile=request.POST.get('mobile'),
#             alt_mobile=request.POST.get('alt_mobile'),
#             pincode=request.POST.get('pincode'),
#             state=request.POST.get('state'),
#             district=request.POST.get('district'),
#             block=request.POST.get('block'),
#             address=request.POST.get('address'),
#             is_default=True
#         )

#         # ✅ Ensure checkout flow
#         if 'checkout_type' not in request.session:
#             request.session['checkout_type'] = 'cart'

#         return redirect('checkout_summary')
@login_required
def save_address(request):
    if request.method == 'POST':

        # 🔥 If address already exists → just mark default
        existing = UserAddress.objects.filter(
            user=request.user,
            mobile=request.POST.get('mobile'),
            pincode=request.POST.get('pincode'),
            address=request.POST.get('address')
        ).first()

        # make all old addresses non-default
        UserAddress.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)

        if existing:
            existing.is_default = True
            existing.save()
        else:
            UserAddress.objects.create(
                user=request.user,
                name=request.POST.get('name'),
                mobile=request.POST.get('mobile'),
                alt_mobile=request.POST.get('alt_mobile'),
                pincode=request.POST.get('pincode'),
                state=request.POST.get('state'),
                district=request.POST.get('district'),
                block=request.POST.get('block'),
                address=request.POST.get('address'),
                is_default=True
            )

        if 'checkout_type' not in request.session:
            request.session['checkout_type'] = 'cart'

        return redirect('checkout_summary')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, UserAddress

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
    total_amount = 0          # discounted total
    original_total = 0        # original price total
    delivery_total = 0        # 🔥 DELIVERY CHARGE TOTAL

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

        # 🔥 delivery charge (single product)
        delivery_total = product.delivery_charge or 0

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

            # 🔥 ADD EACH PRODUCT DELIVERY CHARGE
            delivery_total += product.delivery_charge or 0

            items.append({
                'product': product,
                'size': size,
                'qty': qty,
                'price': price,
                'item_total': item_total
            })

    discount = original_total - total_amount
    grand_total = total_amount + delivery_total   # 🔥 FINAL TOTAL

    # 🔥 save for payment step
    request.session['order_total'] = float(grand_total)
    request.session['order_discount'] = float(discount)
    request.session['order_items_count'] = len(items)
    request.session['delivery_charge'] = float(delivery_total)

    return render(request, 'checkout/summary.html', {
        'address': address,
        'items': items,
        'original_price': original_total,
        'discount': discount,
        'delivery_charge': delivery_total,   # 🔥 SEND TO TEMPLATE
        'total_amount': grand_total           # 🔥 FINAL
    })


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrderItemRequestForm

@login_required
def checkout_payment(request):
    checkout_type = request.session.get('checkout_type', 'cart')

    items = []
    subtotal = 0
    delivery_total = 0   # 🔥 product-wise delivery sum

    # ================= BUY NOW =================
    if checkout_type == 'buy_now' and request.session.get('buy_now'):
        buy = request.session['buy_now']
        product = get_object_or_404(Product, id=buy['product_id'])

        price = product.discounted_price or product.price
        qty = buy.get('qty', 1)

        total = price * qty
        subtotal = total
        delivery_total = product.delivery_charge * qty  # 🔥

        items.append({
            'product': product,
            'quantity': qty,
            'total_price': total
        })

    # ================= CART =================
    else:
        cart = request.session.get('cart', {})
        for key, qty in cart.items():
            product_id, size = key.split('_')
            product = get_object_or_404(Product, id=product_id)

            price = product.discounted_price or product.price
            total = price * qty

            subtotal += total
            delivery_total += product.delivery_charge * qty  # 🔥

            items.append({
                'product': product,
                'quantity': qty,
                'total_price': total
            })

    total_amount = subtotal + delivery_total

    # 🔥 session save (optional but useful)
    request.session['delivery_charge'] = float(delivery_total)
    request.session['order_total'] = float(total_amount)

    return render(request, 'checkout/payment.html', {
        'cart_items': items,
        'subtotal': subtotal,
        'delivery_charge': delivery_total,
        'total_amount': total_amount
    })



def change_address(request):
    # later: fetch saved addresses from DB
    return render(request, 'checkout/change_address.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import UserAddress  # jaha address model achhi
from django.contrib.auth.decorators import login_required

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)

    if request.method == "POST":
        address.name = request.POST.get("name")
        address.mobile = request.POST.get("mobile")
        address.alt_mobile = request.POST.get("alt_mobile")
        address.pincode = request.POST.get("pincode")

    # ✅ USER INPUT — FINAL
        address.state = request.POST.get("state")
        address.district = request.POST.get("district")
        address.block = request.POST.get("block")   # 🔥 THIS LINE IS KEY
        address.address = request.POST.get("address")

        address.save()
        return redirect("checkout_summary")
    return render(request, 'checkout/edit_address.html', {'address': address})

# views.py
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != "pending":
        messages.warning(request, "Order cannot be cancelled")
        return redirect('cart_history')

    for item in order.items.all():
        if item.product and item.size:
            stock = ProductStock.objects.get(
                product=item.product,
                size=item.size
            )
            stock.stock += item.quantity
            stock.save()

    order.status = "cancelled"
    order.save()

    messages.success(request, "Order cancelled & stock restored")
    return redirect('cart_history')

from django.shortcuts import render, get_object_or_404
from .models import Order

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import OrderItem
from .forms import OrderItemRequestForm


@login_required
def request_order_action(request, item_id, action):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )

    # ✅ Only after delivery
    if item.order.status != "delivered":
        messages.warning(request, "Action allowed only after delivery.")
        return redirect("cart_history")

    # ✅ Prevent duplicate request
    if item.return_requested or item.refund_requested or item.exchange_requested:
        messages.warning(request, "You have already submitted a request for this item.")
        return redirect("cart_history")

    if request.method == "POST":
        form = OrderItemRequestForm(
            request.POST,
            request.FILES,
            instance=item
        )

        if form.is_valid():
            obj = form.save(commit=False)

            # ===== Set request type =====
            if action == "return":
                obj.return_requested = True

            elif action == "refund":
                obj.refund_requested = True

            elif action == "exchange":
                obj.exchange_requested = True
                # Exchange re payment details darkar nahi
                obj.refund_method = None
                obj.upi_id = None
                obj.bank_name = None
                obj.bank_account_number = None
                obj.bank_ifsc = None

            else:
                messages.error(request, "Invalid action.")
                return redirect("cart_history")

            obj.request_status = "pending"
            obj.request_date = timezone.now().date()
            obj.save()

            messages.success(
                request,
                f"{action.capitalize()} request submitted successfully."
            )

            return redirect("order_detail", order_id=item.order.id)

        else:
            # ❌ Form invalid → user dekhiba
            messages.error(request, "Please fill all required fields correctly.")

    else:
        form = OrderItemRequestForm(instance=item)

    context = {
        "item": item,
        "action": action,
        "form": form,
    }
    return render(request, "order_request_form.html", context)

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def process_order_request(request, item_id, approve=True):
    item = get_object_or_404(OrderItem, id=item_id)

    if approve:
        item.request_status = "approved"
        item.processed_date = timezone.now()

        # ✅ RETURN → STOCK ADD
        if item.return_requested:
            if item.product and item.size:
                stock = ProductStock.objects.get(
                    product=item.product,
                    size=item.size
                )
                stock.stock += item.quantity
                stock.save()

            item.order.status = "returned"

        # ❌ REFUND → NO STOCK CHANGE
        elif item.refund_requested:
            item.order.status = "refunded"

        elif item.exchange_requested:
            item.order.status = "exchanged"

        item.order.save()

    else:
        item.request_status = "rejected"
        item.processed_date = timezone.now()

    item.save()
    return redirect('/admin/')

# views.py
# from django.http import HttpResponse
# from .models import State, District, Block
# def ajax_load_states(request):
#     country_id = request.GET.get('country')
#     if not country_id:
#         return HttpResponse("")
#     states = State.objects.filter(country_id=country_id)
#     return HttpResponse(''.join(
#         f'<option value="{s.id}">{s.name}</option>' for s in states
#     ))


# def ajax_load_districts(request):
#     state_id = request.GET.get('state')
#     if not state_id:
#         return HttpResponse("")
#     districts = District.objects.filter(state_id=state_id)
#     return HttpResponse(''.join(
#         f'<option value="{d.id}">{d.name}</option>' for d in districts
#     ))


# def ajax_load_blocks(request):
#     district_id = request.GET.get('district')
#     if not district_id:
#         return HttpResponse("")
#     blocks = Block.objects.filter(district_id=district_id)
#     return HttpResponse(''.join(
#         f'<option value="{b.id}">{b.name}</option>' for b in blocks
#     ))

# from .models import Village

# def ajax_load_villages(request):
#     block_id = request.GET.get('block')
#     if not block_id:
#         return HttpResponse("")
#     villages = Village.objects.filter(block_id=block_id)
#     return HttpResponse(''.join(
#         f'<option value="{v.id}">{v.name}</option>' for v in villages
#     ))
from django.http import HttpResponse
from .models import State, District, Block, Village

def ajax_load_states(request):
    country_id = request.GET.get('country')
    states = State.objects.filter(country_id=country_id)
    return HttpResponse(
        '<option value="">Select State</option>' +
        ''.join(f'<option value="{s.id}">{s.name}</option>' for s in states)
    )

def ajax_load_districts(request):
    state_id = request.GET.get('state')
    districts = District.objects.filter(state_id=state_id)
    return HttpResponse(
        '<option value="">Select District</option>' +
        ''.join(f'<option value="{d.id}">{d.name}</option>' for d in districts)
    )

def ajax_load_blocks(request):
    district_id = request.GET.get('district')
    blocks = Block.objects.filter(district_id=district_id)
    return HttpResponse(
        '<option value="">Select Block</option>' +
        ''.join(f'<option value="{b.id}">{b.name}</option>' for b in blocks)
    )

def ajax_load_villages(request):
    block_id = request.GET.get('block')
    villages = Village.objects.filter(block_id=block_id)
    return HttpResponse(
        '<option value="">Select Village</option>' +
        ''.join(f'<option value="{v.id}">{v.name}</option>' for v in villages)
    )
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Order

def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # temporary response (later PDF baniba)
    response = HttpResponse(
        f"Invoice for Order #{order.id}",
        content_type="text/plain"
    )
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.txt"'
    return response

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import OrderItem


@login_required
def product_invoice(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )

    order = item.order
    product = item.product

    # Store (Seller)
    store = product.store if product and hasattr(product, "store") else None

    # 🔹 Build full store address safely
    store_address = ""
    if store:
        address_parts = [
            store.village.name if store.village else "",
            store.block.name if store.block else "",
            store.district.name if store.district else "",
            store.state.name if store.state else "",
            store.country.name if store.country else "",
        ]
        store_address = ", ".join([p for p in address_parts if p])

    customer = {
        "name": order.delivery_name or order.user.get_full_name(),
        "address": order.delivery_address,
        "mobile": order.delivery_phone,
        "email": order.user.email,
    }

    context = {
        "invoice_date": timezone.now().date(),
        "invoice_number": f"INV-{order.id}-{item.id}",
        "order": order,
        "item": item,

        # ✅ seller
        "store": store,
        "store_address": store_address,

        # ✅ GST from PRODUCT
        "product_gst_number": product.gst_number if product else None,

        "customer": customer,
    }

    return render(
        request,
        "invoice/product_invoice.html",
        context
    )
