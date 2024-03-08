from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.http import HttpRequest

from .models import CustomUser


@receiver(user_logged_in)
def handle_user_login(sender, request: HttpRequest, user: CustomUser, **kwargs):
    request.session["subscriptions"] = [item.username for item in user.subscriptions.all()]
