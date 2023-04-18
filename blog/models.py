from django.db import models

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(db_index=True)
    article = models.TextField()
    image = models.ImageField(upload_to="images/%Y/%m/%d/", blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title
