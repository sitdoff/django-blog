from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, "blog/index.html")


def show_post(request, post_slug):
    return HttpResponse(post_slug)
