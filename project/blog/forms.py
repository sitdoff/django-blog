from django import forms

from .models import Post


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "epigraph", "article", "image", "is_draft")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "epigraph": forms.TextInput(attrs={"class": "form-control"}),
            "article": forms.Textarea(attrs={"class": "form-control"}),
        }


class EditStaffPostForm(AddPostForm):
    class Meta(AddPostForm.Meta):
        fields = ("title", "epigraph", "article", "image", "is_published")
