from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic.list import ListView

from blog.mixins import TitleMixin
from blog.models import Post

from .forms import RegisterUserForm
from .mixins import IsAuthorRequiredMixin
from .models import CustomUser

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


class EditProfileUser(IsAuthorRequiredMixin, TitleMixin, UpdateView):
    title = "Данные автора"
    model = CustomUser
    template_name = "users/profile_edit.html"
    fields = ("photo", "first_name", "bio")

    def get_object(self, queryset=None):
        return self.request.user


class AuthorPosts(TitleMixin, ListView):
    model = Post
    template_name = "users/author_posts.html"
    context_object_name = "posts"
    paginate_by = 5

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.title = f"Посты автора {self.kwargs['username']}"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["author"] = get_object_or_404(CustomUser, username=self.kwargs["username"])
        return context

    def get_queryset(self):
        return Post.objects.filter(author__username=self.kwargs["username"]).filter(is_published=True)
