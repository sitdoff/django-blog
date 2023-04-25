from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterUserForm


# Create your views here.
class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "blog/register.html"
    success_url = reverse_lazy("home")


class LoginUser(LoginView):
    template_name = "blog/login.html"
    next_page = reverse_lazy("home")


class LogoutUser(LogoutView):
    ...
