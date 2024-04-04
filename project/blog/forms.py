from django import forms
from django.contrib import messages

from .models import Post
from .tasks import (
    send_mail_your_post_has_been_published_task,
    send_mail_your_post_has_been_returned_task,
)
from .validators import validate_unique_title


class AddPostForm(forms.ModelForm):
    """Form for add post"""

    STATUS_CHOICES = (
        ("is_draft", "Черновик"),
        ("is_unpublished", "Опубликовать"),
        ("delete_draft", "Удалить черновик"),
    )

    status = forms.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        """Metadata"""

        model = Post
        fields = ("title", "epigraph", "article", "image")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "epigraph": forms.TextInput(attrs={"class": "form-control"}),
            "article": forms.Textarea(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_title(self):
        """
        Validate title and slug field
        """
        field_value = self.cleaned_data.get("title")
        if self.instance.pk is not None:
            if self.instance.title != self.cleaned_data.get("title"):
                validate_unique_title(field_value)
        else:
            validate_unique_title(field_value)
        return field_value

    def save(self, commit=True):
        """
        Sets the post status depending on the value passed from the form.
        """
        instance: Post = super().save(commit=False)

        if not hasattr(instance, "author"):
            instance.author = self.request.user

        if self.cleaned_data["status"] == "is_draft":
            messages.info(self.request, "Вы сохранили черновик")
        if self.cleaned_data["status"] == "is_unpublished":
            instance.is_draft = False
            messages.info(self.request, "Ваш пост отправлен на публикацию")

        if commit:
            if self.cleaned_data["status"] == "delete_draft":
                if instance.pk:
                    instance.delete()
                messages.warning(self.request, "Вы удалили черновик")
            else:
                instance.save()

        return instance


class EditStaffPostForm(forms.ModelForm):
    """Form for editing post"""

    STATUS_CHOICES = (
        ("is_unpublished", "Неопубликованный"),
        ("is_draft", "Вернуть автору"),
        ("is_published", "Опубликовать"),
    )

    status = forms.ChoiceField(choices=STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Sets the post status depending on the value passed from the form.
        """
        instance: Post = super().save(commit=False)
        if self.cleaned_data["status"] == "is_draft":
            instance.is_draft = True
            messages.info(self.request, "Вы отправили пост обратно автору")
            send_mail_your_post_has_been_returned_task.delay(instance.id)
        if self.cleaned_data["status"] == "is_published":
            instance.is_published = True
            messages.info(self.request, "Вы опубликовали пост")
            send_mail_your_post_has_been_published_task.delay(instance.id)
        if commit:
            instance.save()
        return instance

    class Meta(AddPostForm.Meta):
        """Metadata"""

        fields = ("title", "epigraph", "article", "image", "status")


class FeedbackForm(forms.Form):
    name = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"id": "name", "class": "form-control", "placeholder": "Name"})
    )
    email = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={"id": "email", "class": "form-control", "placeholder": "Email"})
    )
    subject = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"id": "subject", "class": "form-control", "placeholder": "Subject"}),
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"id": "message", "class": "form-control", "rows": 5, "placeholder": "Message"}),
    )


class SearchForm(forms.Form):
    text = forms.CharField(
        required=True,
        min_length=2,
        widget=forms.TextInput(attrs={"type": "text", "class": "form-control", "placeholder": "Search..."}),
    )
