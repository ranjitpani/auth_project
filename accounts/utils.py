# import resend
# from django.conf import settings

# # Set Resend API key
# resend.api_key = settings.RESEND_API_KEY


# def send_otp_email(email, otp):
#     subject = "Verify your MofyCart account"

#     html = f"""
#     <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;">
#         <h2 style="color:#111;">Hello 👋</h2>

#         <p>
#             Thank you for registering with <b>MofyCart</b>.
#         </p>

#         <p>Your one-time verification code is:</p>

#         <div style="
#             font-size:28px;
#             font-weight:bold;
#             letter-spacing:4px;
#             background:#f4f6f8;
#             padding:14px;
#             text-align:center;
#             border-radius:8px;
#             margin:20px 0;
#         ">
#             {otp}
#         </div>

#         <p>
#             This code is valid for <b>10 minutes</b>.
#         </p>

#         <p style="color:#666;font-size:13px;">
#             If you didn’t request this, you can safely ignore this email.
#         </p>

#         <hr style="border:none;border-top:1px solid #eee;">

#         <p style="font-size:12px;color:#888;">
#             © {settings.DEFAULT_FROM_EMAIL} <br>
#             MofyCart, India
#         </p>
#     </div>
#     """

#     resend.Emails.send({
#         "from": "MofyCart <hello@mofycart.shop>",
#         "to": [email],
#         "subject": subject,
#         "html": html,
#     })


# def generate_otp():
#     return str(random.randint(100000, 999999))    

# accounts/utils.py
import random
import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp, purpose="verify"):
    """Sends OTP email. purpose: 'verify' or 'reset'"""
    if purpose == "verify":
        subject = "Verify your MofyCart account"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;">
            <h2 style="color:#111;">Hello 👋</h2>
            <p>Thank you for registering with <b>MofyCart</b>.</p>
            <p>Your one-time verification code is:</p>
            <div style="
                font-size:28px;
                font-weight:bold;
                letter-spacing:4px;
                background:#f4f6f8;
                padding:14px;
                text-align:center;
                border-radius:8px;
                margin:20px 0;
            ">{otp}</div>
            <p>This code is valid for <b>10 minutes</b>.</p>
            <p style="color:#666;font-size:13px;">
                If you didn't request this, you can safely ignore this email.
            </p>
        </div>
        """
    else:  # reset
        subject = "Reset your MofyCart password"
        html = f"""
        <p>Hello 👋</p>
        <p>Your password reset OTP is:</p>
        <h2>{otp}</h2>
        <p>This OTP is valid for 10 minutes.</p>
        <p>— Team MofyCart</p>
        """
    resend.Emails.send({
        "from": "MofyCart <hello@mofycart.shop>",
        "to": [email],
        "subject": subject,
        "html": html,
    })

from math import radians, cos, sin, asin, sqrt
from decimal import Decimal

from decimal import Decimal
from math import radians, sin, cos, sqrt, asin

def calculate_distance_km(lat1, lon1, lat2, lon2):
    # Ensure values exist
    if not lat1 or not lon1 or not lat2 or not lon2:
        return Decimal(0)
    
    # convert to float
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    
    # convert degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c  # Earth radius
    return Decimal(str(round(km, 2)))

def calculate_km_delivery_charge(store_lat, store_lng, user_lat, user_lng):
    distance_km = calculate_distance_km(store_lat, store_lng, user_lat, user_lng)
    
    # ----------- NEW TIERED DELIVERY CHARGE -----------
    if distance_km <= 2:
        charge = Decimal(20)
    elif distance_km <= 3:
        charge = Decimal(30)
    elif distance_km <= 4:
        charge = Decimal(40)
    else:
        charge = Decimal(40)  # Max delivery charge for >4 km
    
    return distance_km, charge