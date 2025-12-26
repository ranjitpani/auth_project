from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .utils import send_otp_email
import random
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import random

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import random

User = get_user_model()

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm_password']

        if password != confirm:
            return render(request, 'signup.html', {'error': "Passwords do not match"})

        # ✅ Check if email already verified
        if User.objects.filter(email=email, is_verified=True).exists():
            return render(request, 'signup.html', {'error': "Email already registered"})

        # ✅ Check if OTP already sent & session active
        signup_data = request.session.get('signup_data')
        if signup_data and signup_data.get('email') == email:
            return render(request, 'signup.html', {'error': "OTP already sent. Please check your email."})

        # Generate OTP
        otp = random.randint(100000, 999999)
        request.session['signup_data'] = {
            'email': email,
            'password': password,
            'otp': otp
        }

        send_mail(
            'Your OTP Code',
            f'Your OTP is {otp}',
            'your_email@example.com',  # replace with your email
            [email],
            fail_silently=False
        )

        return redirect('verify_otp')

    return render(request, 'signup.html')

def verify_otp(request):
    signup_data = request.session.get('signup_data')
    if not signup_data:
        return redirect('signup')

    if request.method == 'POST':
        user_otp = request.POST['otp']
        if str(signup_data['otp']) == user_otp:
            # Create user only if not already exists
            if not User.objects.filter(email=signup_data['email']).exists():
                user = User.objects.create_user(
                    email=signup_data['email'],
                    password=signup_data['password'],
                    is_verified=True
                )
            del request.session['signup_data']
            return redirect('home')  # redirect to home after OTP verified
        else:
            return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_otp.html')

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


@login_required
def home(request):
    return render(request, 'home.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# accounts/views.py

import random
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect

User = get_user_model()

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            otp = random.randint(100000, 999999)
            request.session['reset_otp_data'] = {
                'email': email,
                'otp': str(otp)
            }
            send_mail(
                'Reset Password OTP',
                f'Your OTP is {otp}',
                'your-email@example.com',
                [email],
                fail_silently=False
            )
            return redirect('verify_reset_otp')
        else:
            return render(request, 'forgot_password.html', {'error': 'Email not found'})
    return render(request, 'forgot_password.html')

# Step 2: Verify OTP
def verify_reset_otp(request):
    data = request.session.get('reset_otp_data')
    if not data:
        return redirect('forgot_password')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == data['otp']:
            request.session['reset_email'] = data['email']
            request.session.pop('reset_otp_data', None)
            return redirect('reset_password')
        else:
            return render(request, 'verify_reset_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_reset_otp.html')

# Step 3: Reset Password
def reset_password(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        if password != confirm:
            return render(request, 'reset_password.html', {'error': 'Passwords do not match'})

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        request.session.pop('reset_email', None)
        return redirect('login')

    return render(request, 'reset_password.html')