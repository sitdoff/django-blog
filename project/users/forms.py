from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegisterUserForm(UserCreationForm):
    """Form for register users"""

    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={"class": "form-register"}))
    email = forms.CharField(label="Адрес электронной почты", widget=forms.EmailInput(attrs={"class": "form-register"}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-register"}))
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput(attrs={"class": "form-register"}))

    def save(self, commit=True):
        """Set password for user object"""
        user = super().save(commit=False)
        return user

    class Meta:
        """Metadata"""

        model = CustomUser
        fields = ("username", "email", "password1", "password2")
