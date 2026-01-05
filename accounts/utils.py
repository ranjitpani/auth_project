import resend
from django.conf import settings

# Set Resend API key
resend.api_key = settings.RESEND_API_KEY


def send_otp_email(email, otp):
    subject = "Verify your MofyCart account"

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;">
        <h2 style="color:#111;">Hello 👋</h2>

        <p>
            Thank you for registering with <b>MofyCart</b>.
        </p>

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
        ">
            {otp}
        </div>

        <p>
            This code is valid for <b>10 minutes</b>.
        </p>

        <p style="color:#666;font-size:13px;">
            If you didn’t request this, you can safely ignore this email.
        </p>

        <hr style="border:none;border-top:1px solid #eee;">

        <p style="font-size:12px;color:#888;">
            © {settings.DEFAULT_FROM_EMAIL} <br>
            MofyCart, India
        </p>
    </div>
    """

    resend.Emails.send({
        "from": "MofyCart <hello@mofycart.shop>",
        "to": [email],
        "subject": subject,
        "html": html,
    })