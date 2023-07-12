from pprint import pprint

from django.core.signing import Signer
from django.shortcuts import reverse
from django.test import TestCase

from blog.models import Post
from blog.tests import CreateTestUsersAndPostsMixin
from neuron.settings import ALLOWED_HOSTS
from users.models import CustomUser
from users.utils import send_activation_notification
from users.views import user_activate

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
            url = reverse(page, kwargs=self.pages[page]["kwargs"])
            for user in self.test_users:
                self.page_test(user=user, url=url, access=self.pages[page]["access"])
            print(f'\nPermissions page "{url}" OK', end="")

    def page_test(self, user=None, url=None, access=None):
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
    def setUp(self):
        self.signer = Signer()
        self.user: CustomUser = CustomUser.objects.create(
            username="user_in_not_active", email="user_is_not_active@test.com", is_active=False
        )
        self.sign: Signer = self.signer.sign(self.user.username)
        if ALLOWED_HOSTS:
            self.host = "http://" + ALLOWED_HOSTS[0]
        else:
            self.host = "http://localhost:8000"

    def test_activate_user(self):
        signer = Signer()
        sign: Signer = signer.sign(self.user.username)
        if ALLOWED_HOSTS:
            host = "http://" + ALLOWED_HOSTS[0]
        else:
            host = "http://localhost:8000"
        request_path: str = host + reverse("users:register_activate", kwargs={"sign": sign})

        response = self.client.get(request_path, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/user/activate/" + signer.sign(self.user.username))
        pprint(response.__dict__)
        print(self.user.username, self.user.is_active)
        self.assertEqual(self.user.is_active, True)
