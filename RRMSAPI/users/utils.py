import random
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_password_setup_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    frontend_link = f"https://rrms-frontend.vercel.app/set-password?uid={uid}&token={token}"

    message = Mail(
        from_email='gaya3budha@gmail.com',
        to_emails=user.email,
        subject='[RRMS] Confirm your Password',
        plain_text_content=f"Hello {user.first_name},\n\nClick the link below to set your password:\n{frontend_link}\n\nThis link is valid for one-time use only."
    )
    # subject = "[RRMS] Confirm your Password"
    # message = f"Hello {user.first_name},\n\nClick the link below to set your password:\n{frontend_link}\n\nThis link is valid for one-time use only."
    # from_email = settings.DEFAULT_FROM_EMAIL
    
    # send_mail(subject, message, from_email, [user.email], fail_silently=False)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.send(message)
    except Exception as e:
        print(e)
        raise

def send_password_reset_email(user,to_email=None):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    frontend_link = f"https://rrms-frontend.vercel.app/set-password?uid={uid}&token={token}"

    subject = "[RRMS] Confirm your Password"
    message = f"Hello {user.first_name},\n\nClick the link below to set your password:\n{frontend_link}\n\nThis link is valid for one-time use only."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient = to_email or user.email

    send_mail(subject, message, from_email, [recipient], fail_silently=False)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_email, otp):
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        '[RRMS] Your OTP for Password Reset',
        f'Your OTP is {otp}. It is valid for 10 minutes.',
        from_email,
        [user_email],
        fail_silently=False,
    )