from django.contrib import admin

from .models import Post


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    empty_value_display = "Пусто"
    readonly_fields = ("time_create", "time_update")
    fields = (
        "title",
        "slug",
        "epigraph",
        "article",
        "author",
        "image",
        "time_create",
        "time_update",
        "is_draft",
        "is_published",
        "is_pinned",
    )
    list_display = ("title", "author", "image", "time_create", "time_update", "is_draft", "is_published", "is_pinned")
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Post, PostAdmin)
