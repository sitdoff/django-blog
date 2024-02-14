from django.apps import apps
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

# Rules for replacing characters in slug
slug_replacements = (("|", "or"), ("%", "percent"))


def send_mail_your_post_has_been_returned(post_id):
    """
    Generate mail and send to user's email
    """
    post = get_object_or_404(apps.get_model("blog", "Post"), pk=post_id)
    context = {"post": post, "author": post.author}
    subject = render_to_string("blog/email/your_post_has_been_returned_subject.txt", context)
    body_text = render_to_string("blog/email/your_post_has_been_returned_body.txt", context)
    post.author.email_user(subject.strip(), body_text)


def send_mail_your_post_has_been_published(post_id):
    """
    Generate mail and send to user's email
    """
    post = get_object_or_404(apps.get_model("blog", "Post"), pk=post_id)
    context = {"post": post, "author": post.author}
    subject = render_to_string("blog/email/your_post_has_been_published_subject.txt", context)
    body_text = render_to_string("blog/email/your_post_has_been_published_body.txt", context)
    post.author.email_user(subject.strip(), body_text)
