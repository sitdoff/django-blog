from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("post/<slug:post_slug>", views.show_post, name="post"),
]
