from django.core.signing import Signer
from django.template.loader import render_to_string

from neuron.settings import ALLOWED_HOSTS

signer = Signer()


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/username/<filename>
    return f"userpic/{instance.username}/{filename}"


def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = "http://" + ALLOWED_HOSTS[0]
    else:
        host = "http://localhost:8000"
    context = {"user": user, "host": host, "sign": signer.sign(user.username)}
    subject = render_to_string("email/activation_letter_subject.txt", context)
    body_text = render_to_string("email/activation_letter_body.txt", context)
    user.email_user(subject.strip(), body_text)
