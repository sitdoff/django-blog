from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("about", views.about, name="about"),
    path("gallery", views.gallery, name="gallery"),
    path("contact", views.contact, name="contact"),
    path("add", views.AddPost.as_view(), name="add_post"),
    path("post/unpublished", views.UnpublishedPostsView.as_view(), name="unpublished_post"),
    path("post/<slug:post_slug>", views.PostDetailView.as_view(), name="post"),
    path("post/edit/<slug:post_slug>", views.EditPost.as_view(), name="edit_post"),
]
