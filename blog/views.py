from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .forms import AddPostForm, EditStaffPostForm
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
    queryset = Post.objects.filter(is_published=True).order_by("-time_update")


class UnpublishedPostsView(IsStaffRequiredMixin, TitleMixin, ListView):
    title = "Неопубликованные посты"
    model = Post
    template_name = "blog/unpublished_posts.html"
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
    form_class = AddPostForm
    template_name = "blog/addpost.html"

    def form_valid(self, form):
        self.instanse = form.save(commit=False)
        self.instanse.author = self.request.user
        self.instanse.save()
        return super().form_valid(form)


class EditPost(IsStaffRequiredMixin, TitleMixin, UpdateView):
    title = "Редактирование поста"
    model = Post
    form_class = EditStaffPostForm
    template_name = "blog/editpost.html"
    slug_url_kwarg = "post_slug"


def about(request):
    return HttpResponse("about")


def gallery(request):
    return HttpResponse("gallery")


def contact(request):
    return HttpResponse("contact")
