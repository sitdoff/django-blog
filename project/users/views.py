from blog.mixins import TitleMixin
from blog.models import Post
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.signing import BadSignature
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic.list import ListView

from .forms import RegisterUserForm
from .mixins import IsAuthorRequiredMixin
from .models import CustomUser
from .utils import signer

# Create your views here.


class RegisterUser(TitleMixin, CreateView):
    """
    Create user
    """

    title = "Регистрация"
    form_class = RegisterUserForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:activation_mail_sended")


class LoginUser(TitleMixin, LoginView):
    """
    Login user
    """

    title = "Вход"
    template_name = "users/login.html"
    next_page = reverse_lazy("home")


class LogoutUser(LogoutView):
    """
    Logout user
    """

    ...


class EditProfileUser(IsAuthorRequiredMixin, TitleMixin, UpdateView):
    """
    Edits user profile
    """

    title = "Данные автора"
    model = CustomUser
    template_name = "users/profile_edit.html"
    fields = ("photo", "first_name", "bio")

    def get_object(self, queryset=None):
        """
        Returns user object
        """
        return self.request.user


class AuthorPosts(TitleMixin, ListView):
    """Author's posts"""

    model = Post
    template_name = "users/author_posts.html"
    context_object_name = "posts"
    paginate_by = 5

    def setup(self, *args, **kwargs) -> None:
        """Adds title attribute"""
        super().setup(*args, **kwargs)
        self.title = f"Посты автора {self.kwargs['username']}"

    def get_context_data(self, *args, **kwargs) -> dict:
        """Adds author in context"""
        context = super().get_context_data(*args, **kwargs)
        context["author"] = get_object_or_404(CustomUser, username=self.kwargs["username"])
        return context

    def get_queryset(self) -> QuerySet:
        """Returns a set of posts"""
        return Post.objects.filter(author__username=self.kwargs["username"]).filter(is_published=True)


def user_activate(request: HttpRequest, sign: str) -> HttpResponse:
    """Checks sign and activates user."""
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, "users/bad_signature.html")

    user: CustomUser = get_object_or_404(CustomUser, username=username)

    if user.is_active:
        template = "users/user_is_active.html"
    else:
        template = "users/activation_done.html"
        user.activate()
        user.save()
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)

    return render(request, template)


def subscribe(request: HttpRequest, author_username: str):
    """
    Add author in user's subscriptions
    """
    author = get_object_or_404(CustomUser, username=author_username, is_author=True)
    if author in request.user.subscriptions.all():
        return JsonResponse(
            {
                "message": f"Вы уже подписаны на {author}",
                "message_level": settings.MESSAGE_TAGS[messages.WARNING],
            },
            json_dumps_params={"ensure_ascii": False},
        )

    request.user.subscriptions.add(author)
    return JsonResponse(
        {
            "message": f"Вы подписались на автора {author_username}",
            "message_level": settings.MESSAGE_TAGS[messages.SUCCESS],
        },
        json_dumps_params={"ensure_ascii": False},
    )
