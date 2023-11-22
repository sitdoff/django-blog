from blog.tests import CreateTestUsersAndPostsMixin
from django.core.signing import Signer
from django.shortcuts import reverse
from django.test import TestCase
from django.test.client import Client
from users.models import CustomUser

from neuron.settings import ALLOWED_HOSTS

# Create your tests here.
# Users for tests


class TestPermissions(CreateTestUsersAndPostsMixin, TestCase):
    """Test pages with permissions"""

    # key - url name
    # value - access
    pages = {
        "add_post": {"access": ("author", "authorstaff", "admin"), "kwargs": {}},
        "drafts": {"access": ("author", "authorstaff", "admin"), "kwargs": {}},
        "unpublished_posts": {"access": ("staff", "authorstaff", "admin"), "kwargs": {}},
        "draft": {"access": ("author", "admin"), "kwargs": {"post_slug": "draft-post"}},
        "edit_draft": {"access": ("author", "admin"), "kwargs": {"post_slug": "draft-post"}},
        "unpublished_post": {"access": ("staff", "authorstaff", "admin"), "kwargs": {"post_slug": "unpublished-post"}},
        "edit_post": {"access": ("staff", "authorstaff", "admin"), "kwargs": {"post_slug": "unpublished-post"}},
        "users:profile_edit": {"access": ("author", "authorstaff", "admin"), "kwargs": {}},
    }

    def test_permissions(self):
        """Main test method"""

        for page in self.pages:
            url: str = reverse(page, kwargs=self.pages[page]["kwargs"])
            for user in self.test_users:
                self.page_test(user=user, url=url, access=self.pages[page]["access"])
            print(f'\nPermissions page "{url}" OK', end="")

    def page_test(self, user=None, url: str | None = None, access=None):
        """Request method"""

        self.client.logout()
        if user:
            self.client.force_login(user)
        response = self.client.get(url)
        if not user:
            self.assertEqual(
                response.status_code, 302, f"\n\nUrl: '{url}'.\nUser: {user}.\nStatus code: {response.status_code}"
            )
            self.assertRedirects(response, f"/user/login?next={url}")
        elif user.username in access:
            self.assertEqual(
                response.status_code, 200, f"\n\nUrl: '{url}'.\nUser: {user}.\nStatus code: {response.status_code}"
            )
        else:
            self.assertEqual(
                response.status_code, 403, f"\n\nUrl: '{url}'.\nUser: {user}.\nStatus code: {response.status_code}"
            )


class TestActivateUser(TestCase):
    """
    Checks user activation via link
    """

    def setUp(self):
        """
        Prepares data for the test
        """
        self.client = Client()

        # initial user data
        self.username = "user_in_not_active"
        self.email = "user_is_not_active@test.com"
        self.password = "user_password"

        # Creating user
        CustomUser.objects.create(username="user_in_not_active", email="user_is_not_active@test.com")

    def test_activating_user(self):
        """
        Activating user account using link in the email
        """
        user: CustomUser = CustomUser.objects.get(username=self.username)
        self.assertEqual(user.is_active, False)

        signer = Signer()
        sign: Signer = signer.sign(user.username)
        if ALLOWED_HOSTS:
            host = "http://" + ALLOWED_HOSTS[0]
        else:
            host = "http://localhost:8000"
        request_path: str = host + reverse("users:register_activate", kwargs={"sign": sign})

        response = self.client.get(request_path, follow=True)

        user: CustomUser = CustomUser.objects.get(username=self.username)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/user/activate/" + signer.sign(user.username))
        self.assertEqual(user.is_active, True)
