from blog.models import Post
from django.shortcuts import reverse
from django.test import TestCase
from users.models import CustomUser

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
        {"username": "admin", "email": "admin@test.com", "is_superuser": True, "is_active": True},
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
