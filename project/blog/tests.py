from blog.models import Post
from django.core import mail
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.test import TestCase, RequestFactory
from slugify import slugify
from users.models import CustomUser
from django.contrib.sessions.middleware import SessionMiddleware

from .utils import (
    send_mail_your_post_has_been_published,
    send_mail_your_post_has_been_returned,
)
from .views import SubscriptionsView

# Create your tests here.


class CreateTestUsersAndPostsMixin:
    """
    Create users and post's objects for tests
    """

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
        "draft2": {"title": "draft_post_second", "is_draft": True, "is_published": False},
        "unpublished": {"title": "unpublished_post", "is_draft": False, "is_published": False},
        "published": {"title": "published_post", "is_draft": False, "is_published": True},
    }

    def setUp(self):
        """
        Create users and posts from class's data
        """

        self.test_users = [None]
        self.test_posts = []

        for user_data in self.users:
            user = CustomUser.objects.create(**user_data)
            self.test_users.append(user)

        author = CustomUser.objects.get(username="author")
        for post_data in self.posts:
            post = Post.objects.create(author=author, **self.posts[post_data])
            self.test_posts.append(post)

class AccessMixin:
    """
    Mixin сontains methods for testing status codes for a specific URL.
    """

    def access_test_with_all_users(
        self,
        url,
        none_user_status_code,
        user_status_code,
        author_status_code,
        staff_status_code,
        authorstaff_status_code,
        admin_status_code,
    ):
        """
        Makes a GET request to the specified URL on behalf of all users and compares the response status code with the specified one.
        """

        self.client.logout()

        for user in self.test_users:
            if user is not None:
                self.client.force_login(user)
            response = self.client.get(url)
            if user is None:
                self.assertEqual(response.status_code, none_user_status_code)
                self.assertRedirects(response, expected_url=reverse("users:login") + f"?next={url}")
            elif not user.is_author and not user.is_staff:
                self.assertEqual(response.status_code, user_status_code)
            elif user.is_author and user.is_staff:
                self.assertEqual(response.status_code, authorstaff_status_code)
            elif user.is_author:
                self.assertEqual(response.status_code, author_status_code)
            elif user.is_staff and not user.is_superuser:
                self.assertEqual(response.status_code, staff_status_code)
            elif user.is_superuser:
                self.assertEqual(response.status_code, admin_status_code)
            self.client.logout()


class TestBlog(CreateTestUsersAndPostsMixin, AccessMixin, TestCase):
    """
    Checks the availability of public pages
    """

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
        """
        Creates addresses of public pages and checks their availability.
        """
        for url_name in self.pages:
            url = reverse(url_name, kwargs=self.pages[url_name]["kwargs"])
            response = self.client.get(url)
            self.assertEqual(response.request["PATH_INFO"], self.pages[url_name]["url"])
            self.assertEqual(response.status_code, 200, f"\n\nUrl is {url}.\nStaus-code is {response.status_code}")
            print(f'Page "{url}" OK')

    def test_access_add_post(self):
        test_data = {
            "url": reverse('add_post'),
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 200,
            "staff_status_code": 403,
            "authorstaff_status_code": 200,
            "admin_status_code": 200,
        }
        self.access_test_with_all_users(**test_data)

    def test_access_edit_draft(self):
        test_data = {
            "url": reverse('edit_draft', kwargs={"post_slug": "draft-post"}),
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 200,
            "staff_status_code": 403,
            "authorstaff_status_code": 403,
            "admin_status_code": 200,
        }
        self.access_test_with_all_users(**test_data)

    def test_edit_unpublished_post(self):
        test_data = {
            "url": reverse('edit_unpublished_post', kwargs={"post_slug": "unpublished-post"}),
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 403,
            "staff_status_code": 200,
            "authorstaff_status_code": 200,
            "admin_status_code": 200,
        }
        self.access_test_with_all_users(**test_data)



class TestAddPostView(TestCase):
    """
    Add post view tests
    """

    def test_add_post_as_draft(self):
        """
        Add post as draft test
        """
        user_data = {"username": "author", "email": "author@test.com", "is_author": True, "is_active": True}
        author = CustomUser.objects.create(**user_data)
        is_post = Post.objects.filter(author=author, slug="draft-post").exists()
        self.assertEqual(is_post, False)

        self.client.force_login(author)
        response = self.client.get(reverse("add_post"))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "title": "draft_post",
            "epigraph": "draft_post",
            "article": "draft_post",
            "image": "",
            "status": "is_draft",
        }

        response = self.client.post(reverse("add_post"), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("drafts"))
        is_post = Post.objects.filter(author=author, slug="draft-post").exists()
        self.assertEqual(is_post, True)

        post = Post.objects.get(slug="draft-post")
        self.assertEqual(post.title, form_data["title"])
        self.assertEqual(post.slug, slugify(form_data["title"]))
        self.assertEqual(post.epigraph, form_data["epigraph"])
        self.assertEqual(post.article, form_data["article"])
        self.assertEqual(post.author, author)
        self.assertEqual(post.is_draft, True)
        self.assertEqual(post.is_published, False)

    def test_add_post_as_unpublished(self):
        """
        Add post as unpublished post test
        """
        user_data = {"username": "author", "email": "author@test.com", "is_author": True, "is_active": True}
        author = CustomUser.objects.create(**user_data)
        is_post = Post.objects.filter(author=author, slug="draft-post").exists()
        self.assertEqual(is_post, False)

        self.client.force_login(author)
        response = self.client.get(reverse("add_post"))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "title": "unpublished_post",
            "epigraph": "unpublished_post",
            "article": "unpublished_post",
            "image": "",
            "status": "is_unpublished",
        }

        response = self.client.post(reverse("add_post"), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("drafts"))
        is_post = Post.objects.filter(author=author, slug="unpublished-post").exists()
        self.assertEqual(is_post, True)

        post = Post.objects.get(slug="unpublished-post")
        self.assertEqual(post.title, form_data["title"])
        self.assertEqual(post.slug, slugify(form_data["title"]))
        self.assertEqual(post.epigraph, form_data["epigraph"])
        self.assertEqual(post.article, form_data["article"])
        self.assertEqual(post.author, author)
        self.assertEqual(post.is_draft, False)
        self.assertEqual(post.is_published, False)

    def test_add_post_with_existing_title(self):
        """
        Testing validation of title uniqueness when creating a new post.
        """
        user_data = {"username": "author", "email": "author@test.com", "is_author": True, "is_active": True}
        author = CustomUser.objects.create(**user_data)
        self.client.force_login(author)

        form_data = {
            "title": "draft_post",
            "epigraph": "draft_post",
            "article": "draft_post",
            "image": "",
            "status": "is_draft",
        }
        response = self.client.post(reverse("add_post"), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("drafts"))

        is_exist = Post.objects.filter(title="draft_post").exists()
        self.assertEqual(is_exist, True)

        response = self.client.post(reverse("add_post"), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пост с таким заголовком уже существует")


class TestEditDraftPostView(CreateTestUsersAndPostsMixin, AccessMixin, TestCase):
    """
    Test EditDraftPostView
    """

    def test_draft_in_edit_draft_view(self):
        """
        Test view with a draft.
        """
        test_data = {
            "url": reverse("edit_draft", kwargs={"post_slug": "draft-post"}),
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 200,
            "staff_status_code": 403,
            "authorstaff_status_code": 403,  # Пост принадлежит другому автору, поэтому доступ запрещен
            "admin_status_code": 200,  # Админ может редактировать любой черновик
        }
        self.access_test_with_all_users(**test_data)

    def test_unpublished_post_in_edit_draft_view(self):
        """
        Test view with an unpublished post.
        """
        test_data = {
            "url": reverse("edit_draft", kwargs={"post_slug": "unpublished-post"}),
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 404,
            "staff_status_code": 403,
            "authorstaff_status_code": 403,
            "admin_status_code": 404,
        }
        self.access_test_with_all_users(**test_data)
    
    def test_published_post_in_edit_draft_view(self):
        """
        Test view with a published post.
        """
        test_data = {
            "url": reverse("edit_draft", kwargs={"post_slug": "published-post"}),
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 404,
            "staff_status_code": 403,
            "authorstaff_status_code": 403,
            "admin_status_code": 404,
        }
        self.access_test_with_all_users(**test_data)

    def test_subscription(self):
        """
        Test view with subscriptions.
        """
        test_data = {
            "url": reverse("subscriptions"),
            "none_user_status_code": 302,
            "user_status_code": 200,
            "author_status_code": 200,
            "staff_status_code": 200,
            "authorstaff_status_code": 200,
            "admin_status_code": 200,
        }
        self.access_test_with_all_users(**test_data)


    def test_save_draft_as_draft(self):
        """
        Testing draft editing. The status of the post remains draft.
        """
        author = CustomUser.objects.get(username="author")
        old_post = Post.objects.get(slug="draft-post")
        self.assertEqual(old_post.author, author)
        self.assertEqual(old_post.title, self.posts["draft"]["title"])
        self.assertEqual(old_post.slug, slugify(self.posts["draft"]["title"]))
        self.assertEqual(old_post.is_draft, self.posts["draft"]["is_draft"])
        self.assertEqual(old_post.is_published, self.posts["draft"]["is_published"])

        self.client.force_login(author)
        response = self.client.get(reverse("edit_draft", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "title": "edited_draft_post",
            "epigraph": "edited_draft_post",
            "article": "edited_draft_post",
            "image": "",
            "status": "is_draft",
        }
        response = self.client.post(reverse("edit_draft", kwargs={"post_slug": old_post.slug}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("drafts"))

        edited_post = Post.objects.get(slug=slugify(form_data["title"]))
        self.assertEqual(old_post.pk, edited_post.pk)
        self.assertEqual(edited_post.title, form_data["title"])
        self.assertEqual(edited_post.slug, slugify(form_data["title"]))
        self.assertEqual(edited_post.epigraph, form_data["epigraph"])
        self.assertEqual(edited_post.article, form_data["article"])
        self.assertEqual(edited_post.author, author)
        self.assertEqual(edited_post.is_draft, True)
        self.assertEqual(edited_post.is_published, False)

    def test_save_draft_as_unpublished_post(self):
        """
        Testing draft editing. The post status becomes "unpublished".
        """
        author = CustomUser.objects.get(username="author")
        old_post = Post.objects.get(slug="draft-post")
        self.assertEqual(old_post.author, author)
        self.assertEqual(old_post.title, self.posts["draft"]["title"])
        self.assertEqual(old_post.slug, slugify(self.posts["draft"]["title"]))
        self.assertEqual(old_post.is_draft, self.posts["draft"]["is_draft"])
        self.assertEqual(old_post.is_published, self.posts["draft"]["is_published"])

        self.client.force_login(author)
        response = self.client.get(reverse("edit_draft", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "title": "edited_draft_post",
            "epigraph": "edited_draft_post",
            "article": "edited_draft_post",
            "image": "",
            "status": "is_unpublished",
        }
        response = self.client.post(reverse("edit_draft", kwargs={"post_slug": old_post.slug}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("drafts"))

        edited_post = Post.objects.get(slug=slugify(form_data["title"]))
        self.assertEqual(old_post.pk, edited_post.pk)
        self.assertEqual(edited_post.title, form_data["title"])
        self.assertEqual(edited_post.slug, slugify(form_data["title"]))
        self.assertEqual(edited_post.epigraph, form_data["epigraph"])
        self.assertEqual(edited_post.article, form_data["article"])
        self.assertEqual(edited_post.author, author)
        self.assertEqual(edited_post.is_draft, False)
        self.assertEqual(edited_post.is_published, False)

    def test_save_draft_with_existing_title(self):
        """
        Test the installation of a post of an existing title.
        """
        is_exits_first = Post.objects.filter(title="draft_post").exists()
        self.assertTrue(is_exits_first)

        is_exits_second = Post.objects.filter(title="draft_post_second").exists()
        self.assertTrue(is_exits_second)

        first_post = Post.objects.get(title="draft_post")
        second_post = Post.objects.get(title="draft_post_second")
        self.assertNotEqual(first_post.title, second_post.title)

        user = CustomUser.objects.get(username="author")
        self.client.force_login(user)

        form_data = {
            "title": "draft_post",
            "epigraph": "draft_post",
            "article": "draft_post",
            "image": "",
            "status": "is_draft",
        }
        response = self.client.post(
            reverse("edit_draft", kwargs={"post_slug": slugify("draft_post_second")}), data=form_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пост с таким заголовком уже существует")

        is_exits_first = Post.objects.filter(title="draft_post").exists()
        self.assertTrue(is_exits_first)

        is_exits_second = Post.objects.filter(title="draft_post_second").exists()
        self.assertTrue(is_exits_second)

        first_post = Post.objects.get(title="draft_post")
        second_post = Post.objects.get(title="draft_post_second")
        self.assertNotEqual(first_post.title, second_post.title)

    def test_change_status_exitst_draft(self):
        """
        Test changing the post title to an existing one.
        """
        post = Post.objects.get(slug="draft-post")
        user = CustomUser.objects.get(username="author")
        self.client.force_login(user)

        form_data = {
            "title": "draft_post",
            "epigraph": "draft_post",
            "article": "draft_post",
            "image": "",
            "status": "is_unpublished",
        }
        response = self.client.post(reverse("edit_draft", kwargs={"post_slug": "draft-post"}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("drafts"))

        post = Post.objects.get(slug="draft-post")
        self.assertEqual(post.is_draft, False)
        self.assertEqual(post.is_published, False)

    def test_delete_draft(self):
        """
        Test draft deletion.
        """
        user = CustomUser.objects.get(username="author")
        self.client.force_login(user)

        is_exist = Post.objects.filter(slug="draft-post").exists()
        self.assertEqual(is_exist, True)

        form_data = {
            "title": "draft_post",
            "epigraph": "draft_post",
            "article": "draft_post",
            "image": "",
            "status": "delete_draft",
        }
        response = self.client.post(reverse("edit_draft", kwargs={"post_slug": "draft-post"}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("drafts"))

        is_exist = Post.objects.filter(slug="draft-post").exists()
        self.assertEqual(is_exist, False)

    def test_set_to_draft_published_status(self):
        """
        Test installation of draft status published.
        """
        post = Post.objects.get(slug="draft-post")
        self.assertTrue(post.is_draft)
        self.assertFalse(post.is_published)

        author = CustomUser.objects.get(username="author")
        self.client.force_login(author)

        form_data = {
            "title": "draft_post",
            "epigraph": "draft_post",
            "article": "draft_post",
            "image": "",
            "status": "is_published",
        }
        response = self.client.post(reverse("edit_draft", kwargs={"post_slug": post.slug}), data=form_data)
        self.assertEqual(response.status_code, 200)

        post = Post.objects.get(slug="draft-post")
        self.assertTrue(post.is_draft)
        self.assertFalse(post.is_published)


class TestEditUnpublishedPostViews(CreateTestUsersAndPostsMixin, AccessMixin, TestCase):
    """
    EditUnpublishedPost View tests.
    """

    def test_draft_in_edit_unpublished_post_view(self):
        """
        Testing with a draft.
        """
        test_data = {
            "url": reverse("edit_unpublished_post", kwargs={"post_slug": "draft-post"}),
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 403,
            "staff_status_code": 404,
            "authorstaff_status_code": 404,
            "admin_status_code": 404,
        }
        self.access_test_with_all_users(**test_data)

    def test_unpublished_post_in_unpublished_post_view(self):
        """
        Testing with an unpublished post.
        """
        test_data = {
            "url": reverse("edit_unpublished_post", kwargs={"post_slug": "unpublished-post"}),
            "none_user_status_code": 302,
            "user_status_code": 403,
            "author_status_code": 403,
            "staff_status_code": 200,
            "authorstaff_status_code": 200,
            "admin_status_code": 200,
        }
        self.access_test_with_all_users(**test_data)

    def test_published_post_in_unpublished_post_view(self):
        """
        Testing with a published post.
        """
        test_data = {
            "url": reverse("edit_unpublished_post", kwargs={"post_slug": "published-post"}),
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
        Test editing an unpublished post.
        """
        user = CustomUser.objects.get(username="staff")
        old_post = Post.objects.get(slug="unpublished-post")
        self.assertEqual(old_post.title, "unpublished_post")
        self.assertEqual(old_post.is_draft, False)
        self.assertEqual(old_post.is_published, False)

        self.client.force_login(user)
        response = self.client.get(reverse("edit_unpublished_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "title": "edited_post",
            "epigraph": "edited_post",
            "article": "edited_post",
            "image": "",
            "status": "is_unpublished",
        }
        response = self.client.post(
            reverse("edit_unpublished_post", kwargs={"post_slug": old_post.slug}), data=form_data
        )
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
        Test returning an unpublished post to the author's draft.
        """
        staff = CustomUser.objects.get(username="staff")
        author = CustomUser.objects.get(username="author")
        old_post = Post.objects.get(slug="unpublished-post")
        self.assertEqual(old_post.title, "unpublished_post")
        self.assertEqual(old_post.is_draft, False)
        self.assertEqual(old_post.is_published, False)

        self.client.force_login(staff)
        response = self.client.get(reverse("edit_unpublished_post", kwargs={"post_slug": old_post.slug}))
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
        response = self.client.post(
            reverse("edit_unpublished_post", kwargs={"post_slug": old_post.slug}), data=form_data
        )
        updated_post = Post.objects.get(pk=old_post.pk)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("unpublished_posts"))
        self.assertNotEqual(updated_post.title, old_post.title)
        self.assertEqual(updated_post.title, "edited_post")
        self.assertEqual(updated_post.epigraph, "edited_post")
        self.assertEqual(updated_post.article, "edited_post")
        self.assertEqual(updated_post.is_draft, True)
        self.assertEqual(updated_post.is_published, False)

        response = self.client.get(reverse("edit_unpublished_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("edit_unpublished_post", kwargs={"post_slug": updated_post.slug}))
        self.assertEqual(response.status_code, 404)

        self.client.force_login(author)
        response = self.client.get(reverse("edit_unpublished_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("edit_draft", kwargs={"post_slug": updated_post.slug}))
        self.assertEqual(response.status_code, 200)

    def test_publishing_post(self):
        """
        Test publishing an unpublished post.
        """
        user = CustomUser.objects.get(username="staff")
        old_post = Post.objects.get(slug="unpublished-post")
        self.assertEqual(old_post.title, "unpublished_post")
        self.assertEqual(old_post.is_draft, False)
        self.assertEqual(old_post.is_published, False)

        self.client.force_login(user)
        response = self.client.get(reverse("edit_unpublished_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "title": "edited_post",
            "epigraph": "edited_post",
            "article": "edited_post",
            "image": "",
            "status": "is_published",
        }
        response = self.client.post(
            reverse("edit_unpublished_post", kwargs={"post_slug": old_post.slug}), data=form_data
        )
        updated_post = Post.objects.get(pk=old_post.pk)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("unpublished_posts"))
        self.assertNotEqual(updated_post.title, old_post.title)
        self.assertEqual(updated_post.title, "edited_post")
        self.assertEqual(updated_post.epigraph, "edited_post")
        self.assertEqual(updated_post.article, "edited_post")
        self.assertEqual(updated_post.is_draft, False)
        self.assertEqual(updated_post.is_published, True)

        response = self.client.get(reverse("edit_unpublished_post", kwargs={"post_slug": old_post.slug}))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("edit_unpublished_post", kwargs={"post_slug": updated_post.slug}))
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


class TestSubscriptionsView(CreateTestUsersAndPostsMixin, TestCase):
    """
    Test SubscriptionsView
    """
    def test_queryset(self):
        """
        Test only published posts in quetyset
        """
        request_factory = RequestFactory()
        request = request_factory.get(reverse("subscriptions"))
        request.user = CustomUser.objects.get(username='user')

        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        request.session.save()

        request.session['subscriptions'] = ['author']
        request.session.save()

        view = SubscriptionsView()
        view.setup(request)
        quetyset = view.get_queryset()

        for post in quetyset:
            self.assertTrue(post.is_published)

    def test_view(self):
        """
        Test page before and after subscribe
        """
        user = CustomUser.objects.get(username='user')
        author = CustomUser.objects.get(username='author')
        self.client.force_login(user)
        
        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Вы еще ни на кого не подписаны", response.content.decode("utf-8"))

        self.client.get(reverse("users:subscribe", kwargs={"author_username": author.username}))

        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, 200)
        for post in author.author_posts.filter(is_published=True)[:5]:
            self.assertIn(post.title, response.content.decode('utf-8'))

    
