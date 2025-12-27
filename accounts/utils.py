import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY

def send_otp_email(email, otp):
    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": email,
        "subject": "Your OTP Code",
        "html": f"""
            <h2>Your OTP is {otp}</h2>
            <p>This OTP is valid for 5 minutes.</p>
        """,
    })