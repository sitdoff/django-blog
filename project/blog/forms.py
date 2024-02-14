from django import forms
from django.contrib import messages

from .models import Post
from .tasks import (
    send_mail_your_post_has_been_published_task,
    send_mail_your_post_has_been_returned_task,
)

STATUS_CHOICES = (
    ("is_unpublished", "Неопубликованный"),
    ("is_draft", "Вернуть автору"),
    ("is_published", "Опубликовать"),
)


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

    status = forms.ChoiceField(choices=STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=False):
        instance: Post = super().save(commit=False)
        if self.cleaned_data["status"] == "is_draft":
            instance.is_draft = True
            instance.save()
            messages.info(self.request, "Вы отправили пост обратно автору")
            send_mail_your_post_has_been_returned_task.delay(instance.id)
        if self.cleaned_data["status"] == "is_published":
            instance.is_published = True
            instance.save()
            messages.info(self.request, "Вы опубликовали пост")
            send_mail_your_post_has_been_published_task.delay(instance.id)
        return instance

    class Meta(AddPostForm.Meta):
        """Metadata"""

        fields = ("title", "epigraph", "article", "image", "is_published", "status")
