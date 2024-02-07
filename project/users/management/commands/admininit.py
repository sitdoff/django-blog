import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

UserModel = get_user_model()

load_dotenv()


class Command(BaseCommand):
    """
    Command to create a superuser.
    """

    def handle(self, *args, **options):
        if UserModel.objects.count() == 0:
            username = os.getenv("SUPERUSER_USERNAME")
            email = os.getenv("SUPERUSER_EMAIL")
            password = os.getenv("SUPERUSER_PASSWORD")
            print(f"Creating account for {username} ({email})")
            admin = UserModel.objects.create_superuser(email=email, username=username, password=password)
            admin.save()
        else:
            print("Admin account already initialized")
