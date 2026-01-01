# # utils.py
# import resend
# from django.conf import settings

# # API key setup (live use pai)
# resend.api_key = settings.RESEND_API_KEY

# def send_otp_email(email, otp, live=False):
#     """
#     Send OTP email.
#     - live=False -> print OTP in terminal (local testing)
#     - live=True  -> send email via Resend
#     """
#     if live:
#         try:
#             resend.Emails.send({
#                 "from": settings.DEFAULT_FROM_EMAIL,
#                 "to": email,
#                 "subject": "Your OTP Code",
#                 "html": f"""
#                     <h2>Your OTP is {otp}</h2>
#                     <p>This OTP is valid for 5 minutes.</p>
#                 """,
#             })
#             print(f"OTP sent successfully to {email}")
#         except Exception as e:
#             print(f"Error sending OTP: {e}")
#     else:
#         # Local testing: just print in terminal
#         print(f"Sending OTP to: {email} OTP: {otp}")
import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY

def send_otp_email(email, otp):
    resend.Emails.send({
        "from": "hello@mofycart.shop",
        "to": [email],
        "subject": "Your OTP Code",
        "html": f"""
        <h2>OTP Verification</h2>
        <p>Your OTP is:</p>
        <h1>{otp}</h1>
        <p>This OTP is valid for 5 minutes.</p>
        """
    })