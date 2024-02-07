from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from .managers import CustomUserManager
from .utils import user_directory_path

# Create your models here.


class CustomUser(AbstractUser):
    """
    Custom user model with extra fields
    """

    id: int
    email = models.EmailField(unique=True, blank=False)
    photo = models.ImageField(
        upload_to=user_directory_path, blank=True, verbose_name="Фотография", default="userpic/default/default.jpg"
    )
    bio = models.TextField(blank=True, verbose_name="О себе")
    is_author = models.BooleanField(default=False, verbose_name="Статус автора")
    is_active = models.BooleanField(default=False, verbose_name="Активен")
    is_banned = models.BooleanField(default=False, verbose_name="Заблокирован")
    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        """
        Return url on object
        """
        return reverse("users:author_posts", kwargs={"username": self.username})

    def activate(self):
        """
        Activate user
        """
        if not self.is_banned:
            self.is_active = True

    class Meta:
        """
        Metadata
        """

        verbose_name = "Пользователя"
        verbose_name_plural = "Пользователи"
