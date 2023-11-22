from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse

from .utils import user_directory_path

# Create your models here.


class CustomUserManager(BaseUserManager):
    """
    Custom User Manager for CustomUser
    """

    def create_user(self, username, password=None, **other_fields):
        """
        Create common user
        """
        if not other_fields["email"]:
            raise ValueError("User must have an email address")
        user = self.model(username=username, email=self.normalize_email(other_fields["email"]))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **other_fields):
        """
        Create superuser
        """
        user = self.create_user(username, password, **other_fields)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


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
