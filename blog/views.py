from django.http import HttpResponse
from django.shortcuts import render

from .models import Post


# Create your views here.
def index(request):
    posts = Post.objects.all()
    context = {"posts": posts}
    return render(request, "blog/index.html", context=context)


def show_post(request, post_slug):
    return render(request, "blog/single_post.html")
