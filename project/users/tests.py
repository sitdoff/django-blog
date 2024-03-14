import json

from blog.tests import CreateTestUsersAndPostsMixin
from django.contrib.auth.models import AnonymousUser
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
from users.views import subscribe, unsubscribe

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

    @classmethod
    def setUpTestData(cls):
        """
        Create users
        """
        for user_data in cls.users:
            CustomUser.objects.create(**user_data)

    @classmethod
    def setUpClass(cls):
        """
        Assigns a value to class attributes.
        """
        super().setUpClass()

        cls.user = CustomUser.objects.get(username="user")
        cls.user.set_password("password")
        cls.user.save()
        cls.author = CustomUser.objects.get(username="author")

    @staticmethod
    def get_request(user: CustomUser | AnonymousUser):
        """
        Create request
        """
        request_factory = RequestFactory()

        request = request_factory.get("/")
        request.user = user

        if not isinstance(user, AnonymousUser):
            middleware = SessionMiddleware(lambda request: None)
            middleware.process_request(request)
            request.session["subscriptions"] = []
            request.session.save()

            middleware = MessageMiddleware(lambda request, response: None)
            middleware.process_request(request)

        return request

    def setUp(self):
        self.request = self.get_request(self.user)

    def tearDown(self):
        """
        Remove relations
        """
        self.user.subscriptions.remove(self.author)

    def test_subscription_field_for_user(self):
        """
        Test the "subscriptions" field in the CustomUser model for common user.
        """
        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(self.author, self.user.subscriptions.all())

        self.user.subscriptions.add(self.author)
        self.assertEqual(self.user.subscriptions.count(), 1)
        self.assertIn(self.author, self.user.subscriptions.all())
        self.assertEqual(self.user.subscriptions.all()[0], self.author)

    def test_subscription_field_for_author(self):
        """
        Test the "subscriptions" field in the CustomUser model for author.
        """
        self.assertEqual(self.author.subscribers.count(), 0)
        self.assertNotIn(self.user, self.author.subscribers.all())

        self.user.subscriptions.add(self.author)
        self.assertEqual(self.author.subscribers.count(), 1)
        self.assertIn(self.user, self.author.subscribers.all())
        self.assertEqual(self.author.subscribers.all()[0], self.user)

    def test_subscribe_function_if_username_is_owned_by_author(self):
        """
        Tests the "subscribe" function if the author_username is owned by the author.
        """
        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(self.author, self.user.subscriptions.all())

        response = subscribe(self.request, self.author.username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.subscriptions.count(), 1)
        self.assertIn(self.author, self.user.subscriptions.all())
        json_response = json.loads(response.content)
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], f"Вы подписались на автора {self.author.username}")
        self.assertNotEqual(json_response["message"], f"{self.author.username} не является автором")
        self.assertEqual(self.request.session["subscriptions"], [self.author.username])

        response = subscribe(self.request, self.author.username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.subscriptions.count(), 1)
        self.assertIn(self.author, self.user.subscriptions.all())
        json_response = json.loads(response.content)
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], f"Вы уже подписаны на {self.author.username}")
        self.assertNotEqual(json_response["message"], f"Вы подписались на автора {self.author.username}")
        self.assertNotEqual(json_response["message"], f"{self.author.username} не является автором")
        self.assertEqual(self.request.session["subscriptions"], [self.author.username])

    def test_subscribe_function_if_username_is_not_owned_by_author(self):
        """
        Tests the "subscribe" function if the author_username is't owned by the author.
        """
        not_author = CustomUser.objects.get(username="staff")
        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(not_author, self.user.subscriptions.all())

        with self.assertRaises(Http404):
            subscribe(self.request, not_author.username)
        self.assertNotEqual(self.request.session["subscriptions"], [not_author])
        self.assertEqual(self.request.session["subscriptions"], [])

    def test_subscribe_function_if_username_does_not_exist(self):
        """
        Tests the "subscribe" function if the author_username dosen't exist
        """
        do_not_exist = "super_author"
        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(do_not_exist, self.user.subscriptions.all())

        with self.assertRaises(Http404):
            subscribe(self.request, do_not_exist)
        self.assertNotEqual(self.request.session["subscriptions"], [do_not_exist])
        self.assertEqual(self.request.session["subscriptions"], [])

    def test_subscribe_function_if_user_is_anonymous(self):
        """
        Tests the "subscribe" function if the user is anonymous
        """
        user = AnonymousUser()

        self.request = self.get_request(user)

        response = subscribe(self.request, self.author.username)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], "Неавторизованные пользователи не могут подписываться")
        self.assertNotEqual(json_response["message"], f"Вы подписались на автора {self.author.username}")
        self.assertNotEqual(json_response["message"], f"{self.author.username} не является автором")

    def test_subscribe_by_url_if_username_is_owned_by_author(self):
        """
        Testing a subscription to the author.
        """
        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(self.author, self.user.subscriptions.all())

        self.client.force_login(self.user)

        response = self.client.get(reverse("users:subscribe", kwargs={"author_username": self.author.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.subscriptions.count(), 1)
        self.assertIn(self.author, self.user.subscriptions.all())

    def test_subscribe_by_url_if_username_is_not_owned_by_author(self):
        """
        Testing a subscription not to the author.
        """
        not_author = CustomUser.objects.get(username="staff")

        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(self.author, self.user.subscriptions.all())

        self.client.force_login(self.user)

        response = self.client.get(reverse("users:subscribe", kwargs={"author_username": not_author.username}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(not_author, self.user.subscriptions.all())

    def test_get_subscribe_data_in_session_when_anon_user_subscribe_by_url(self):
        """
        Test adding data to a session when an anonymous user tries to subscribe to the author.
        """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertIsNone(self.client.session.get("subscriptions"))

        response = self.client.get(reverse("users:subscribe", kwargs={"author_username": self.author.username}))
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.client.session.get("subscriptions"), ["author"])

    def test_get_subscribe_data_in_session_when_common_user_subscribe_by_url(self):
        """
        Test adding data to a session when a common user tries to subscribe to the author.
        """
        response = self.client.post(
            reverse("users:login"), data={"username": "user", "password": "password"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertIsNotNone(self.client.session.get("subscriptions"))
        self.assertEqual(self.client.session.get("subscriptions"), [])

        response = self.client.get(reverse("users:subscribe", kwargs={"author_username": self.author.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get("subscriptions"), ["author"])

    def test_get_subscribe_data_in_session_when_user_login(self):
        """
        Test of adding data to a session when a common user logs in.
        """
        response = self.client.post(
            reverse("users:login"), data={"username": "user", "password": "password"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertIsNotNone(self.client.session.get("subscriptions"))
        self.assertEqual(self.client.session.get("subscriptions"), [])

        response = self.client.get(reverse("users:subscribe", kwargs={"author_username": self.author.username}))
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


class TestUnsubscribe(CreateTestUsersAndPostsMixin, TestCase):
    """
    Test unsubscriptions for authors.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create users
        """
        for user_data in cls.users:
            CustomUser.objects.create(**user_data)

    @classmethod
    def setUpClass(cls):
        """
        Assigns a value to class attributes.
        """
        super().setUpClass()

        cls.user = CustomUser.objects.get(username="user")
        cls.author = CustomUser.objects.get(username="author")

    @staticmethod
    def get_request(user: CustomUser | AnonymousUser):
        """
        Create request
        """
        request_factory = RequestFactory()

        request = request_factory.get("/")
        request.user = user

        if not isinstance(user, AnonymousUser):
            middleware = SessionMiddleware(lambda request: None)
            middleware.process_request(request)
            request.session["subscriptions"] = ["author"]
            request.session.save()

            middleware = MessageMiddleware(lambda request, response: None)
            middleware.process_request(request)

        return request

    def setUp(self):
        self.user.subscriptions.add(self.author)
        self.request = self.get_request(self.user)

    def test_unsubscribe_function_if_username_is_owned_by_author(self):
        """
        Tests the "unsubscribe" function if the author_username is owned by the author.
        """
        response = unsubscribe(self.request, self.author.username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(self.author, self.user.subscriptions.all())
        json_response = json.loads(response.content)
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], f"Вы отписались от автора {self.author.username}")
        self.assertNotEqual(json_response["message"], "Неавторизованные пользователи не могут отписываться")
        self.assertNotEqual(json_response["message"], f"Вы не подписаны на {self.author}")
        self.assertNotEqual(self.request.session["subscriptions"], [self.author.username])
        self.assertEqual(self.request.session["subscriptions"], [])

    def test_unsubscribe_function_if_username_is_not_owned_by_author(self):
        """
        Tests the "unsubscribe" function if the author_username is't owned by the author.
        """
        not_author = CustomUser.objects.get(username="staff")

        response = unsubscribe(self.request, not_author.username)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(not_author, self.user.subscriptions.all())
        json_response = json.loads(response.content)
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], f"Вы не подписаны на {not_author}")
        self.assertNotEqual(json_response["message"], f"Вы отписались от автора {not_author.username}")
        self.assertNotEqual(json_response["message"], "Неавторизованные пользователи не могут отписываться")
        self.assertEqual(self.request.session["subscriptions"], ["author"])

    def test_unsubscribe_function_if_username_does_not_exist(self):
        """
        Tests the "unsubscribe" function if the author_username dosen't exist
        """
        do_not_exist = "super_author"

        with self.assertRaises(Http404):
            unsubscribe(self.request, do_not_exist)
        self.assertEqual(self.request.session["subscriptions"], ["author"])

    def test_unsubscribe_function_if_username_does_not_in_subscriptions(self):
        """
        Tests the "unsubscribe" function if the author_username does not in user's subscriptions.
        """
        self.user.subscriptions.remove(self.author)
        self.request.session["subscriptions"].remove(self.author.username)

        response = unsubscribe(self.request, self.author.username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(self.author, self.user.subscriptions.all())
        json_response = json.loads(response.content)
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], f"Вы не подписаны на {self.author}")
        self.assertNotEqual(json_response["message"], f"Вы отписались от автора {self.author.username}")
        self.assertNotEqual(json_response["message"], "Неавторизованные пользователи не могут отписываться")
        self.assertEqual(self.request.session["subscriptions"], [])

    def test_unsubscribe_function_if_user_is_anonymous(self):
        """
        Tests the "unsubscribe" function if the user is anonymous
        """
        user = AnonymousUser()

        request = self.get_request(user)

        response = unsubscribe(request, self.author.username)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], "Неавторизованные пользователи не могут отписываться")
        self.assertNotEqual(json_response["message"], f"Вы не подписаны на {self.author}")
        self.assertNotEqual(json_response["message"], f"Вы отписались от автора {self.author.username}")

    def test_unsubscribe_by_url_if_username_is_owned_by_author(self):
        """
        Testing a unsubscription to the author.
        """
        self.assertEqual(self.user.subscriptions.count(), 1)
        self.assertIn(self.author, self.user.subscriptions.all())

        self.client.force_login(self.user)

        response = self.client.get(reverse("users:unsubscribe", kwargs={"author_username": self.author.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(self.author, self.user.subscriptions.all())

    def test_unsubscribe_by_url_if_username_is_not_owned_by_author(self):
        """
        Testing a unsubscription not to the author.
        """
        self.assertEqual(self.user.subscriptions.count(), 1)
        self.assertIn(self.author, self.user.subscriptions.all())

        self.client.force_login(self.user)

        response = self.client.get(reverse("users:unsubscribe", kwargs={"author_username": self.author.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.subscriptions.count(), 0)
        self.assertNotIn(self.author, self.user.subscriptions.all())

    def test_delete_subscribe_data_in_session_when_common_user_unsubscribe_by_url(self):
        """
        Test deleting data to a session when a common user tries to unsubscribe to the author.
        """
        self.assertEqual(self.user.subscriptions.count(), 1)
        self.assertIn(self.author, self.user.subscriptions.all())

        self.client.force_login(self.user)

        response = self.client.get(reverse("users:unsubscribe", kwargs={"author_username": self.author.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get("subscriptions"), [])
