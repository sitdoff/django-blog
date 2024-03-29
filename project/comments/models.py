from django.db import models

# Create your models here.


class Comment(models.Model):
    """Comment's model"""

    content = models.TextField(verbose_name="Текст комментария")
    post = models.ForeignKey("blog.Post", on_delete=models.CASCADE, verbose_name="Пост")
    author = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, verbose_name="Автор")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовать?")

    def __str__(self):
        return f"{self.post.title} - {self.author.username} - {self.content[:20]}"

    def cut_content(self):
        """Returns the first 50 characters of a comment"""
        cut = self.content[:50]
        return cut + ("..." if len(cut) == 50 else "")

    class Meta:
        """Metadata"""

        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["time_create"]
