from django import forms
from slugify import slugify

from .models import Post


def validate_unique_title(title):
    """
    Checks the uniqueness of the entered title.
    """
    is_title_exist = Post.objects.filter(title=title).exists()
    is_slug_exist = Post.objects.filter(slug=slugify(title)).exists()

    if is_title_exist or is_slug_exist:
        raise forms.ValidationError("Пост с таким заголовком уже существует")
