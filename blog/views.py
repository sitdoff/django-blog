from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .forms import PostForm
from .models import Post


# Create your views here.
class IndexView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "posts"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Главная страница"
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/single_post.html"
    context_object_name = "post"
    slug_url_kwarg = "post_slug"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = context["post"]
        return context


class AddPost(CreateView):
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
