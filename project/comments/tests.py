from blog.models import Post
from blog.tests import CreateTestUsersAndPostsMixin
from django.test import TestCase
from users.models import CustomUser

from .models import Comment

# Create your tests here.


class CommentTestCase(CreateTestUsersAndPostsMixin, TestCase):
    """Test comment"""

    def setUp(self):
        super().setUp()
        self.author: CustomUser = CustomUser.objects.get(username="author")
        self.post: Post = Post.objects.create(title="post", is_draft=False, is_published=True, author=self.author)
        self.comment: Comment = Comment.objects.create(
            content="Привет", post=self.post, author=self.author, is_published=True
        )

    def test_comment_create(self):
        """Tests comment's creation"""
        self.assertEqual(self.comment.content, "Привет")
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author, self.author)
        self.assertEqual(self.comment.is_published, True)

    def test_comment_get_record(self):
        """Test comment's data"""
        test_comment: Comment = Comment.objects.get(pk=2)
        self.assertEqual(self.comment.content, test_comment.content)
        self.assertEqual(self.comment.post, test_comment.post)
        self.assertEqual(self.comment.author, test_comment.author)
        self.assertEqual(self.comment.time_create, test_comment.time_create)
        self.assertEqual(self.comment.is_published, test_comment.is_published)
