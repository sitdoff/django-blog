from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.urls import reverse
from slugify import slugify

from comments.models import Comment

from .utils import slug_replacements

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    slug = models.SlugField(max_length=150, db_index=True, verbose_name="URL SLUG", unique=True)
    epigraph = models.CharField(max_length=256, blank=True, verbose_name="Эпиграф")
    article = RichTextUploadingField(verbose_name="Текст")
    author = models.ForeignKey("users.CustomUser", on_delete=models.PROTECT, verbose_name="Автор")
    image = models.ImageField(upload_to="images/%Y/%m/%d/", blank=True, verbose_name="Титульное изображение")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время редактирования")
    is_draft = models.BooleanField(default=True, verbose_name="Черновик")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовать")
    is_pinned = models.BooleanField(default=False, verbose_name="Закрепить")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post", kwargs={"post_slug": self.slug})

    def get_comments(self):
        return Comment.objects.filter(post=self.pk, is_published=True).select_related()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, word_boundary=True, replacements=slug_replacements)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-time_create"]
