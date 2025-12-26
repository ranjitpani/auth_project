import random
from django.core.mail import send_mail

def generate_otp():
    return random.randint(100000, 999999)

def send_otp_email(email, otp):
    send_mail(
        'Your OTP Code',
        f'Your OTP is {otp}',
        'noreply@authapp.com',
        [email],
        fail_silently=False,
    )