from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={"class": "form-register"}))
    email = forms.CharField(label="Адрес электронной почты", widget=forms.EmailInput(attrs={"class": "form-register"}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-register"}))
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput(attrs={"class": "form-register"}))

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")
