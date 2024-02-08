from celery import shared_task

from .utils import send_activation_notification


@shared_task
def send_activation_email_task(user_id):
    """
    The task is processed in users/forms.py:RegisterUserForm.save()
    """
    return send_activation_notification(user_id)
