from django.dispatch import Signal, receiver
from django.core.mail import send_mail
from .models import UserProfile
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.paginator import Paginator


email_template = settings.BASE_DIR / 'templates/accounts/signup-email.html' 
post_signup_signal = Signal()

@receiver(post_signup_signal, sender=UserProfile)
def send_signup_email(sender, **kwargs):
    try:
        html_message = render_to_string(email_template, {'user': sender.user.full_name})
        plain_message = strip_tags(html_message)

        send_mail(
            'Welcome to Bull Mines',
            plain_message,
            'Bull Mines <no-reply@bullmines.com>', # your cPanel email address
            [sender.user.email], # the recipient's email address
            fail_silently=False,
            html_message=html_message,
        )
    except Exception:
        raise



def paginate_objects(qs, per_page=20, orphans=0):
    paginator = Paginator(qs, per_page, orphans)
    return paginator