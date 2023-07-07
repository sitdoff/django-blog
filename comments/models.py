from django.db import models

# Create your models here.


class Comment(models.Model):
    content = models.TextField(verbose_name="Текст комментария")
    post = models.ForeignKey("blog.Post", on_delete=models.CASCADE, verbose_name="Пост")
    author = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, verbose_name="Автор")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовать?")

    def __str__(self):
        return f"{self.post.title} - {self.author.username} - {self.content[:20]}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
