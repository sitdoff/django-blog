from celery import shared_task

from .utils import (
    send_mail_your_post_has_been_published,
    send_mail_your_post_has_been_returned,
)


@shared_task
def send_mail_your_post_has_been_returned_task(post_id):
    """
    The task is processed in blog/forms.py EditStaffPostForm.save()
    """
    send_mail_your_post_has_been_returned(post_id)


@shared_task
def send_mail_your_post_has_been_published_task(post_id):
    """
    The task is processed in blog/forms.py EditStaffPostForm.save()
    """
    send_mail_your_post_has_been_published(post_id)
