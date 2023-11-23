from django import forms

from .models import Post


class AddPostForm(forms.ModelForm):
    """Form for add post"""

    class Meta:
        """Metadata"""

        model = Post
        fields = ("title", "epigraph", "article", "image", "is_draft")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "epigraph": forms.TextInput(attrs={"class": "form-control"}),
            "article": forms.Textarea(attrs={"class": "form-control"}),
        }


class EditStaffPostForm(AddPostForm):
    """Form for editing post"""

    class Meta(AddPostForm.Meta):
        """Metadata"""

        fields = ("title", "epigraph", "article", "image", "is_published")
