from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from blog.utils import TitleMixin

from .forms import RegisterUserForm


# Create your views here.
class RegisterUser(TitleMixin, CreateView):
    title = "Регистрация"
    form_class = RegisterUserForm
    template_name = "users/register.html"
    success_url = reverse_lazy("home")


class LoginUser(TitleMixin, LoginView):
    title = "Вход"
    template_name = "users/login.html"
    next_page = reverse_lazy("home")


class LogoutUser(LogoutView):
    ...
