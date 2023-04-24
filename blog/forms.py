from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    def __init__(self, author, *args, **kwargs):
        self.author = author
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.author = self.author
        return super().save(*args, **kwargs)

    class Meta:
        model = Post
        fields = (
            "title",
            "epigraph",
            "article",
            "image",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "epigraph": forms.TextInput(attrs={"class": "form-control"}),
            "article": forms.Textarea(attrs={"class": "form-control"}),
            # "image",
            # "is_published",
            # "author",
        }
