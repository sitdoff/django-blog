from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    """Comment's form"""

    class Meta:
        """Metadata"""

        model = Comment
        fields = ("content", "post", "author")
        widgets = {
            "post": forms.HiddenInput,
            "author": forms.HiddenInput,
            "content": forms.Textarea(
                attrs={
                    "name": "message",
                    "rows": 5,
                    "class": "form-control",
                    "id": "message",
                    "placeholder": "Ваш комментарий",
                    "message": "message",
                    "required": "required",
                }
            ),
        }
