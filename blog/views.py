from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView

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


def show_post(request, post_slug):
    return render(request, "blog/single_post.html")
