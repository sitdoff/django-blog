from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("add", views.AddPost.as_view(), name="add_post"),
    path("post/<slug:post_slug>", views.PostDetailView.as_view(), name="post"),
]
