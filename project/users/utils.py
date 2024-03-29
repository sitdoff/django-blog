from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.signing import Signer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

# from .models import CustomUser

# Create signer object
signer = Signer()


def user_directory_path(instance, filename: str) -> str:
    """Returns path for uploaded userpic"""

    # file will be uploaded to MEDIA_ROOT/userpic/username/<filename>
    return f"userpic/{instance.username}/{filename}"


def send_activation_notification(user_id) -> None:
    """Generate mail and send to user's email"""
    user = get_object_or_404(get_user_model(), pk=user_id)
    if settings.ALLOWED_HOSTS:
        host = "http://" + settings.ALLOWED_HOSTS[0]
    else:
        host = "http://localhost:8000"
    context = {"user": user, "host": host, "sign": signer.sign(user.username)}
    subject = render_to_string("email/activation_letter_subject.txt", context)
    body_text = render_to_string("email/activation_letter_body.txt", context)
    user.email_user(subject.strip(), body_text)
