from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "epigraph",
            "article",
            "image",
            "is_published",
            "author",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "epigraph": forms.TextInput(attrs={"class": "form-control"}),
            "article": forms.Textarea(attrs={"class": "form-control"}),
            # "image",
            # "is_published",
            # "author",
        }
