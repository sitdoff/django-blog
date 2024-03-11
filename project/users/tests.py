import json

from blog.tests import CreateTestUsersAndPostsMixin
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.core.signing import Signer
from django.http import HttpRequest
from django.http.response import Http404
from django.shortcuts import reverse
from django.test import Client, RequestFactory, TestCase
from django.test.client import Client
from users.models import CustomUser
from users.views import subscribe

from neuron.settings import ALLOWED_HOSTS

from .utils import send_activation_notification

# Create your tests here.
# Users for tests


class TestPermissions(CreateTestUsersAndPostsMixin, TestCase):
    """Test pages with permissions"""

    # key - url name
    # value - access
    pages = {
        "add_post": {
            "access": ("author", "authorstaff", "admin"),
            "kwargs": {},
        },
        "drafts": {
            "access": ("author", "authorstaff", "admin"),
            "kwargs": {},
        },
        "unpublished_posts": {
            "access": ("staff", "authorstaff", "admin"),
            "kwargs": {},
        },
        "draft": {
            "access": ("author", "admin"),
            "kwargs": {"post_slug": "draft-post"},
        },
        "edit_draft": {
            "access": ("author", "admin"),
            "kwargs": {"post_slug": "draft-post"},
        },
        "unpublished_post": {
            "access": ("staff", "authorstaff", "admin"),
            "kwargs": {"post_slug": "unpublished-post"},
        },
        "edit_unpublished_post": {
            "access": ("staff", "authorstaff", "admin"),
            "kwargs": {"post_slug": "unpublished-post"},
        },
        "users:profile_edit": {
            "access": ("author", "authorstaff", "admin"),
            "kwargs": {},
        },
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
    """Checks user activation via link"""

    def setUp(self):
        """Prepares data for the test"""
        self.client = Client()

        # initial user data
        self.username = "user_in_not_active"
        self.email = "user_is_not_active@test.com"
        self.password = "user_password"

        # Creating user
        CustomUser.objects.create(username="user_in_not_active", email="user_is_not_active@test.com")

    def test_sending_an_activation_mail(self):
        """
        Testing sending an activation letter when registering a user.
        """
        user: CustomUser = CustomUser.objects.get(username=self.username)
        self.assertEqual(user.is_active, False)

        signer = Signer()
        sign: Signer = signer.sign(user.username)

        send_activation_notification(user.id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Активация пользователя user_in_not_active")
        self.assertIn(sign, mail.outbox[0].body)

    def test_activating_user(self):
        """Activating user account using link in the email"""
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


class TestSubscription(CreateTestUsersAndPostsMixin, TestCase):
    """
    Test subscriptions for authors.
    """

    def test_subscription_field_for_user(self):
        """
        Test the "subscriptions" field in the CustomUser model for common user.
        """
        user = CustomUser.objects.get(username="user")
        author = CustomUser.objects.get(username="author")

        self.assertEqual(user.subscriptions.count(), 0)
        self.assertNotIn(author, user.subscriptions.all())

        user.subscriptions.add(author)
        self.assertEqual(user.subscriptions.count(), 1)
        self.assertIn(author, user.subscriptions.all())
        self.assertEqual(user.subscriptions.all()[0], author)

    def test_subscription_field_for_author(self):
        """
        Test the "subscriptions" field in the CustomUser model for author.
        """

        user = CustomUser.objects.get(username="user")
        author = CustomUser.objects.get(username="author")

        self.assertEqual(author.subscribers.count(), 0)
        self.assertNotIn(user, author.subscribers.all())

        user.subscriptions.add(author)
        self.assertEqual(author.subscribers.count(), 1)
        self.assertIn(user, author.subscribers.all())
        self.assertEqual(author.subscribers.all()[0], user)

    def test_subscribe_function_if_username_is_owned_by_author(self):
        """
        Tests the "subscribe" function if the author_username is owned by the author.
        """
        request_factory = RequestFactory()

        user = CustomUser.objects.get(username="user")
        author = CustomUser.objects.get(username="author")
        self.assertEqual(user.subscriptions.count(), 0)
        self.assertNotIn(author, user.subscriptions.all())

        request = request_factory.get("/")
        request.user = user

        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        request.session["subscriptions"] = []
        request.session.save()

        middleware = MessageMiddleware(lambda request, response: None)
        middleware.process_request(request)

        response = subscribe(request, author.username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.subscriptions.count(), 1)
        self.assertIn(author, user.subscriptions.all())
        json_response = json.loads(response.content)
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], f"Вы подписались на автора {author.username}")
        self.assertNotEqual(json_response["message"], f"{author.username} не является автором")

        response = subscribe(request, author.username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.subscriptions.count(), 1)
        self.assertIn(author, user.subscriptions.all())
        json_response = json.loads(response.content)
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], f"Вы уже подписаны на {author.username}")
        self.assertNotEqual(json_response["message"], f"Вы подписались на автора {author.username}")
        self.assertNotEqual(json_response["message"], f"{author.username} не является автором")

    def test_subscribe_function_if_username_is_not_owned_by_author(self):
        """
        Tests the "subscribe" function if the author_username is't owned by the author.
        """
        request_factory = RequestFactory()

        user = CustomUser.objects.get(username="user")
        not_author = CustomUser.objects.get(username="staff")
        self.assertEqual(user.subscriptions.count(), 0)
        self.assertNotIn(not_author, user.subscriptions.all())

        request = request_factory.get("/")
        request.user = user

        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda request, response: None)
        middleware.process_request(request)

        with self.assertRaises(Http404):
            subscribe(request, not_author.username)

    def test_subscribe_function_if_username_does_not_exist(self):
        """
        Tests the "subscribe" function if the author_username dosen't exist
        """
        request_factory = RequestFactory()

        user = CustomUser.objects.get(username="user")
        do_not_exist = "super_author"
        self.assertEqual(user.subscriptions.count(), 0)
        self.assertNotIn(do_not_exist, user.subscriptions.all())
        request = request_factory.get("/")
        request.user = user

        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda request, response: None)
        middleware.process_request(request)

        with self.assertRaises(Http404):
            subscribe(request, do_not_exist)

    def test_subscribe_by_url_if_username_is_owned_by_author(self):
        """
        Testing a subscription to the author.
        """
        user = CustomUser.objects.get(username="user")
        author = CustomUser.objects.get(username="author")

        self.assertEqual(user.subscriptions.count(), 0)
        self.assertNotIn(author, user.subscriptions.all())

        self.client.force_login(user)

        response = self.client.get(reverse("users:subscribe", kwargs={"author_username": author.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.subscriptions.count(), 1)
        self.assertIn(author, user.subscriptions.all())

    def test_subscribe_by_url_if_username_is_not_owned_by_author(self):
        """
        Testing a subscription not to the author.
        """
        user = CustomUser.objects.get(username="user")
        author = CustomUser.objects.get(username="staff")

        self.assertEqual(user.subscriptions.count(), 0)
        self.assertNotIn(author, user.subscriptions.all())

        self.client.force_login(user)

        response = self.client.get(reverse("users:subscribe", kwargs={"author_username": author.username}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(user.subscriptions.count(), 0)
        self.assertNotIn(author, user.subscriptions.all())

    def test_get_subscribe_data_in_session_when_anon_user_subscribe_by_url(self):
        """
        Test adding data to a session when an anonymous user tries to subscribe to the author.
        """
        author = CustomUser.objects.get(username="author")

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertIsNone(self.client.session.get("subscriptions"))

        response = self.client.get(reverse("users:subscribe", kwargs={"author_username": author.username}))
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.client.session.get("subscriptions"), ["author"])

    def test_get_subscribe_data_in_session_when_common_user_subscribe_by_url(self):
        """
        Test adding data to a session when a common user tries to subscribe to the author.
        """
        user = CustomUser.objects.get(username="user")
        user.set_password("password")
        user.save()
        author = CustomUser.objects.get(username="author")

        response = self.client.post(
            reverse("users:login"), data={"username": "user", "password": "password"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertIsNotNone(self.client.session.get("subscriptions"))
        self.assertEqual(self.client.session.get("subscriptions"), [])

        response = self.client.get(reverse("users:subscribe", kwargs={"author_username": author.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get("subscriptions"), ["author"])

    def test_get_subscribe_data_in_session_when_user_login(self):
        """
        Test of adding data to a session when a common user logs in.
        """
        user = CustomUser.objects.get(username="user")
        user.set_password("password")
        user.save()
        author = CustomUser.objects.get(username="author")

        response = self.client.post(
            reverse("users:login"), data={"username": "user", "password": "password"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertIsNotNone(self.client.session.get("subscriptions"))
        self.assertEqual(self.client.session.get("subscriptions"), [])

        response = self.client.get(reverse("users:subscribe", kwargs={"author_username": author.username}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse("users:login"), data={"username": "user", "password": "password"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertIsNotNone(self.client.session.get("subscriptions"))
        self.assertEqual(self.client.session.get("subscriptions"), ["author"])
        self.assertIn("author", self.client.session.get("subscriptions"))
