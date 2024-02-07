from django.contrib.auth.models import BaseUserManager


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
        user.is_author = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
