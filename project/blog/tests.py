from blog.models import Post
from django.core import mail
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.test import TestCase
from users.models import CustomUser

from .utils import (
    send_mail_your_post_has_been_published,
    send_mail_your_post_has_been_returned,
)

# Create your tests here.


class CreateTestUsersAndPostsMixin:
    """Create users and post's objects for tests"""

    users = [
        {"username": "user", "email": "user@test.com", "is_active": True},
        {"username": "author", "email": "author@test.com", "is_author": True, "is_active": True},
        {"username": "staff", "email": "staff@mail.com", "is_staff": True, "is_active": True},
        {
            "username": "authorstaff",
            "email": "authorstaff@test.com",
            "is_author": True,
            "is_staff": True,
            "is_active": True,
        },
        {"username": "admin", "email": "admin@test.com", "is_staff": True, "is_superuser": True, "is_active": True},
    ]
    posts = {
        "draft": {"title": "draft_post", "is_draft": True, "is_published": False},
        "unpublished": {"title": "unpublished_post", "is_draft": False, "is_published": False},
        "published": {"title": "published_post", "is_draft": False, "is_published": True},
    }

    def setUp(self):
        """Create users and posts from class's data"""

        self.test_users = [None]
        self.test_posts = []

        for user_data in self.users:
            user = CustomUser.objects.create(**user_data)
            self.test_users.append(user)

        author = CustomUser.objects.get(username="author")
        for post_data in self.posts:
            post = Post.objects.create(author=author, **self.posts[post_data])
            self.test_posts.append(post)


class TestBlog(CreateTestUsersAndPostsMixin, TestCase):
    """Checks the availability of public pages"""

    pages = {
        "home": {"url": "/", "kwargs": {}},
        "about": {"url": "/about", "kwargs": {}},
        "gallery": {"url": "/gallery", "kwargs": {}},
        "contact": {"url": "/contact", "kwargs": {}},
        "users:register": {"url": "/user/register", "kwargs": {}},
        "users:login": {"url": "/user/login", "kwargs": {}},
        "users:author_posts": {"url": "/user/author/author", "kwargs": {"username": "author"}},
        "post": {"url": "/post/published-post", "kwargs": {"post_slug": "published-post"}},
    }

    def test_pages(self):
        """Creates addresses of public pages and checks their availability."""
        for url_name in self.pages:
            url = reverse(url_name, kwargs=self.pages[url_name]["kwargs"])
            response = self.client.get(url)
            self.assertEqual(response.request["PATH_INFO"], self.pages[url_name]["url"])
            self.assertEqual(response.status_code, 200, f"\n\nUrl is {url}.\nStaus-code is {response.status_code}")
            print(f'Page "{url}" OK')


class TestEditUnpublishedPostViews(CreateTestUsersAndPostsMixin, TestCase):
    """
    EditUnpublishedPost View tests.
    """

    def access_test_with_all_users(
        self,
        post_slug,
        none_user_status_code,
        user_status_code,
        author_status_code,
        staff_status_code,
        authorstaff_status_code,
        admin_status_code,
    ):
        post = Post.objects.get(slug=post_slug)

        self.client.logout()

        for user in self.test_users:
            if user is not None:
                self.client.force_login(user)
            response = self.client.get(reverse("edit_post", kwargs={"post_slug": post.slug}))
            if user is None:
                self.assertEqual(response.status_code, none_user_status_code)
                self.assertRedirects(
                    response, expected_url=reverse("users:login") + f"?next=/unpublished/edit/{post.slug}"
                )
            elif not user.is_author and not user.is_staff:
                self.assertEqual(response.status_code, user_status_code)
            elif user.is_author and user.is_staff:
                self.assertEqual(response.status_code, authorstaff_status_code)
            elif user.is_author:
                self.assertEqual(response.status_code, author_status_code)
            elif user.is_staff:
                self.assertEqual(response.status_code, staff_status_code)
            elif user.is_superuser:
                self.assertEqual(response.status_code, admin_status_code)
            self.client.logout()

    def test_access_unpublished_post(self):
        """
        Testing with an unpublished post.
        """
        test_data = {
            "post_slug": "unpublished-post",
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 403,
            "staff_status_code": 200,
            "authorstaff_status_code": 200,
            "admin_status_code": 200,
        }
        self.access_test_with_all_users(**test_data)

    def test_access_draft(self):
        """
        Testing with a draft.
        """
        test_data = {
            "post_slug": "draft-post",
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 403,
            "staff_status_code": 404,
            "authorstaff_status_code": 404,
            "admin_status_code": 404,
        }
        self.access_test_with_all_users(**test_data)

    def test_access_published_post(self):
        """
        Testing with a published post.
        """
        test_data = {
            "post_slug": "published-post",
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 403,
            "staff_status_code": 404,
            "authorstaff_status_code": 404,
            "admin_status_code": 404,
        }
        self.access_test_with_all_users(**test_data)

    def test_edit_unpublished_post_view(self):
        """
        Tests editing an unpublished post.
        """
        user = CustomUser.objects.get(username="staff")
        old_post = Post.objects.get(slug="unpublished-post")
        self.assertEqual(old_post.title, "unpublished_post")
        self.assertEqual(old_post.is_draft, False)
        self.assertEqual(old_post.is_published, False)

        self.client.force_login(user)
        response = self.client.get(reverse("edit_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "title": "edited_post",
            "epigraph": "edited_post",
            "article": "edited_post",
            "image": "",
            "status": "is_unpublished",
        }
        response = self.client.post(reverse("edit_post", kwargs={"post_slug": old_post.slug}), data=form_data)
        updated_post = Post.objects.get(pk=old_post.pk)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("unpublished_post", kwargs={"post_slug": updated_post.slug}))
        self.assertNotEqual(updated_post.title, old_post.title)
        self.assertEqual(updated_post.title, "edited_post")
        self.assertEqual(updated_post.epigraph, "edited_post")
        self.assertEqual(updated_post.article, "edited_post")
        self.assertEqual(updated_post.is_draft, False)
        self.assertEqual(updated_post.is_published, False)

    def test_return_unpublished_post_to_draft(self):
        """
        Tests returning an unpublished post to the author's draft.
        """
        staff = CustomUser.objects.get(username="staff")
        author = CustomUser.objects.get(username="author")
        old_post = Post.objects.get(slug="unpublished-post")
        self.assertEqual(old_post.title, "unpublished_post")
        self.assertEqual(old_post.is_draft, False)
        self.assertEqual(old_post.is_published, False)

        self.client.force_login(staff)
        response = self.client.get(reverse("edit_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(author)
        response = self.client.get(reverse("edit_draft", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 404)

        self.client.force_login(staff)

        form_data = {
            "title": "edited_post",
            "epigraph": "edited_post",
            "article": "edited_post",
            "image": "",
            "status": "is_draft",
        }
        response = self.client.post(reverse("edit_post", kwargs={"post_slug": old_post.slug}), data=form_data)
        updated_post = Post.objects.get(pk=old_post.pk)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("unpublished_posts"))
        self.assertNotEqual(updated_post.title, old_post.title)
        self.assertEqual(updated_post.title, "edited_post")
        self.assertEqual(updated_post.epigraph, "edited_post")
        self.assertEqual(updated_post.article, "edited_post")
        self.assertEqual(updated_post.is_draft, True)
        self.assertEqual(updated_post.is_published, False)

        response = self.client.get(reverse("edit_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("edit_post", kwargs={"post_slug": updated_post.slug}))
        self.assertEqual(response.status_code, 404)

        self.client.force_login(author)
        response = self.client.get(reverse("edit_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("edit_draft", kwargs={"post_slug": updated_post.slug}))
        self.assertEqual(response.status_code, 200)

    def test_publishing_post(self):
        """
        Tests publishing an unpublished post.
        """
        user = CustomUser.objects.get(username="staff")
        old_post = Post.objects.get(slug="unpublished-post")
        self.assertEqual(old_post.title, "unpublished_post")
        self.assertEqual(old_post.is_draft, False)
        self.assertEqual(old_post.is_published, False)

        self.client.force_login(user)
        response = self.client.get(reverse("edit_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "title": "edited_post",
            "epigraph": "edited_post",
            "article": "edited_post",
            "image": "",
            "status": "is_published",
        }
        response = self.client.post(reverse("edit_post", kwargs={"post_slug": old_post.slug}), data=form_data)
        updated_post = Post.objects.get(pk=old_post.pk)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("unpublished_posts"))
        self.assertNotEqual(updated_post.title, old_post.title)
        self.assertEqual(updated_post.title, "edited_post")
        self.assertEqual(updated_post.epigraph, "edited_post")
        self.assertEqual(updated_post.article, "edited_post")
        self.assertEqual(updated_post.is_draft, False)
        self.assertEqual(updated_post.is_published, True)

        response = self.client.get(reverse("edit_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("edit_post", kwargs={"post_slug": updated_post.slug}))
        self.assertEqual(response.status_code, 404)


class TestSetEditor(CreateTestUsersAndPostsMixin, TestCase):
    """
    Testing the editor assignment view.
    """

    def test_get_set_editor(self):
        """
        Sends a GET request to the set_editor view.
        """
        self.client.logout()
        for user in self.test_users:
            if user is not None:
                self.client.force_login(user)
            response = self.client.get(reverse("set_editor"))
            if user is not None and user.is_staff:
                self.assertEqual(response.status_code, 405)
            else:
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, expected_url=reverse("users:login") + "?next=/unpublished/set_editor")
            self.client.logout()

    def test_post_set_editor(self):
        """
        Sends a POST request to the set_editor view.
        """
        self.client.logout()
        for user in self.test_users:
            if user is not None:
                self.client.force_login(user)
            for post in self.test_posts:
                self.assertEqual(post.editor, None)
                response = self.client.post(reverse("set_editor"), data={"post_slug": post.slug})
                post = Post.objects.get(slug=post.slug)
                if user is not None and user.is_staff and not post.is_published:
                    self.assertEqual(post.editor, user)
                else:
                    self.assertEqual(post.editor, None)
                self.assertEqual(response.status_code, 302)
                post.editor = None
                post.save()
            self.client.logout()

    def test_set_editor_if_post_already_have_editor(self):
        """
        Testing the set_editror view if the post already has an editor.
        """
        editor_data = {"username": "editor", "email": "editor@mail.com", "is_staff": True, "is_active": True}
        editor = CustomUser.objects.create(**editor_data)
        post = Post.objects.get(slug="unpublished-post")
        self.assertEqual(post.editor, None)
        post.editor = editor
        post.save()
        self.client.logout()
        for user in self.test_users:
            if user is not None:
                self.client.force_login(user)
            self.client.get(reverse("set_editor"))
            self.assertNotEqual(editor, user)
            self.assertEqual(post.editor, editor)
            self.client.logout()


class TestSendingLetterToAurhor(CreateTestUsersAndPostsMixin, TestCase):
    """
    Testing sending emails to the author when the editor changes the status of his post.
    """

    def test_send_mail_your_post_has_been_returned(self):
        """
        Testing the function of sending a letter to the author
        when his post is returned to drafts.
        """
        post = Post.objects.get(slug="unpublished-post")
        context = {"post": post, "author": post.author}
        subject = render_to_string("blog/email/your_post_has_been_returned_subject.txt", context)
        body_text = render_to_string("blog/email/your_post_has_been_returned_body.txt", context)
        send_mail_your_post_has_been_returned(post.pk)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject.strip())
        self.assertEqual(mail.outbox[0].body, body_text)

    def test_send_mail_your_post_has_been_published(self):
        """
        Tests the function of sending a letter to the author
        when his post is published.
        """
        post = Post.objects.get(slug="unpublished-post")
        context = {"post": post, "author": post.author}
        subject = render_to_string("blog/email/your_post_has_been_published_subject.txt", context)
        body_text = render_to_string("blog/email/your_post_has_been_published_body.txt", context)
        send_mail_your_post_has_been_published(post.pk)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject.strip())
        self.assertEqual(mail.outbox[0].body, body_text)
