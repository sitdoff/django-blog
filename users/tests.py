from django.shortcuts import reverse
from django.test import TestCase

from blog.models import Post
from blog.tests import CreateTestUsersAndPostsMixin
from users.models import CustomUser

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
        "profile_edit": {"access": ("author", "authorstaff", "admin"), "kwargs": {}},
    }

    def test_permissions(self):
        """Main test method"""

        for page in self.pages:
            url = reverse(page, kwargs=self.pages[page]["kwargs"])
            for user in self.test_users:
                self.page_test(user=user, url=url, access=self.pages[page]["access"])
            print(f'Permissions page "{url}" OK')

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
            self.assertRedirects(response, "/user/login")
        elif user.username in access:
            self.assertEqual(
                response.status_code, 200, f"\n\nUrl: '{url}'.\nUser: {user}.\nStatus code: {response.status_code}"
            )
        else:
            self.assertEqual(
                response.status_code, 403, f"\n\nUrl: '{url}'.\nUser: {user}.\nStatus code: {response.status_code}"
            )
