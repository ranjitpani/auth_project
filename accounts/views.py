from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import random
from django.conf import settings

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

        send_mail(
    'Your OTP Code',
    f'Your OTP is {otp}',
    settings.DEFAULT_FROM_EMAIL,  # ✅ from settings
    [email],
    fail_silently=False
)
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

        send_mail(
    'Your OTP Code',
    f'Your OTP is {otp}',
    settings.DEFAULT_FROM_EMAIL,  # ✅ from settings
    [email],
    fail_silently=False
)
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
    return render(request, 'profile.html')