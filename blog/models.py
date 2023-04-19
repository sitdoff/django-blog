from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.urls import reverse

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    slug = models.SlugField(db_index=True, verbose_name="URL SLUG")
    article = RichTextUploadingField(verbose_name="Текст")
    image = models.ImageField(upload_to="images/%Y/%m/%d/", blank=True, verbose_name="Титульное изображение")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время редактирования")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post", kwargs={"post_slug": self.slug})
