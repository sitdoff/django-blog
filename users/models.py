from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from .utils import user_directory_path

# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    photo = models.ImageField(
        upload_to=user_directory_path, blank=True, verbose_name="Фотография", default="userpic/default/default.jpg"
    )
    bio = models.TextField(blank=True, verbose_name="О себе")
    is_author = models.BooleanField(default=False, verbose_name="Статус автора")
    is_active = models.BooleanField(default=False, verbose_name="Активен?")

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:author_posts", kwargs={"username": self.username})

    class Meta:
        verbose_name = "Пользователя"
        verbose_name_plural = "Пользователи"
