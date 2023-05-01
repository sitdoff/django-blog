from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .forms import PostForm
from .models import Post
from .utils import TitleMixin


# Create your views here.
class IsAuthorRequiredMixin(PermissionRequiredMixin):
    redirect_field_name = None
    login_url = reverse_lazy("login")

    def has_permission(self):
        if self.request.user.is_anonymous or not self.request.user.is_author:
            return False
        return True


class IsStaffRequiredMixin(PermissionRequiredMixin):
    redirect_field_name = None
    login_url = reverse_lazy("login")

    def has_permission(self):
        if self.request.user.is_anonymous or not self.request.user.is_staff:
            return False
        return True


class IndexView(TitleMixin, ListView):
    title = "Главная страница"
    model = Post
    template_name = "blog/index.html"
    paginate_by = 5
    context_object_name = "posts"
    queryset = Post.objects.filter(is_published=True)


class UnpublishedPostsView(IsStaffRequiredMixin, TitleMixin, ListView):
    title = "Неопубликованные посты"
    model = Post
    template_name = "blog/index.html"
    paginate_by = 5
    context_object_name = "posts"
    queryset = Post.objects.filter(is_published=False)


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/single_post.html"
    context_object_name = "post"
    slug_url_kwarg = "post_slug"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = context["post"]
        return context


class AddPost(IsAuthorRequiredMixin, TitleMixin, CreateView):
    title = "Добавить пост"
    form_class = PostForm
    template_name = "blog/addpost.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"author": self.request.user if self.request.user.is_authenticated else None})
        return kwargs


def about(request):
    return HttpResponse("about")


def gallery(request):
    return HttpResponse("gallery")


def contact(request):
    return HttpResponse("contact")
