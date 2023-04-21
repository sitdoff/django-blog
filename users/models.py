from django.contrib.auth.models import AbstractUser
from django.db import models

from .utils import user_directory_path

# Create your models here.


class CustomUser(AbstractUser):
    photo = models.ImageField(upload_to=user_directory_path, blank=True, verbose_name="Фотография")
    bio = models.TextField(blank=True, verbose_name="О себе")
    is_author = models.BooleanField(default=False, verbose_name="Статус автора")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователя"
        verbose_name_plural = "Пользователи"
