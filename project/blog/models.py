from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.urls import reverse
from slugify import slugify

from comments.models import Comment

from .redis_services import get_post_views
from .utils import slug_replacements

# Create your models here.


class Post(models.Model):
    """Post model"""

    title = models.CharField(max_length=150, verbose_name="Заголовок")
    slug = models.SlugField(max_length=150, db_index=True, verbose_name="URL SLUG", unique=True)
    epigraph = models.CharField(max_length=256, blank=True, verbose_name="Эпиграф")

    # ckeditor field
    article = RichTextUploadingField(verbose_name="Текст")

    author = models.ForeignKey(
        "users.CustomUser", on_delete=models.PROTECT, verbose_name="Автор", related_name="author_posts"
    )
    editor = models.ForeignKey(
        "users.CustomUser", on_delete=models.SET_NULL, null=True, verbose_name="Редактор", related_name="editor_posts"
    )
    image = models.ImageField(upload_to="images/%Y/%m/%d/", blank=True, verbose_name="Титульное изображение")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время редактирования")
    is_draft = models.BooleanField(default=True, verbose_name="Черновик")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовать")
    is_pinned = models.BooleanField(default=False, verbose_name="Закрепить")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Return post url"""
        return reverse("post", kwargs={"post_slug": self.slug})

    def get_comments(self):
        """Returns comments"""
        return Comment.objects.filter(post=self.pk, is_published=True).select_related()

    def get_views(self):
        """
        Rerurns views
        """
        return get_post_views(self)

    def save(self, *args, **kwargs):
        """Add custom slug"""
        self.slug = slugify(self.title, word_boundary=True, replacements=slug_replacements)
        return super().save(*args, **kwargs)

    class Meta:
        """Metadata"""

        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-time_create"]
