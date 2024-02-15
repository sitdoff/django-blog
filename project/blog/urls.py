from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("about", views.about, name="about"),
    path("gallery", views.gallery, name="gallery"),
    path("contact", views.contact, name="contact"),
    path("add", views.AddPost.as_view(), name="add_post"),
    path("post/<slug:post_slug>", views.PostDetailView.as_view(), name="post"),
    path("drafts", views.DraftPostsView.as_view(), name="drafts"),
    path("post/draft/<slug:post_slug>", views.DraftPostDetailView.as_view(), name="draft"),
    path("drafts/edit/<slug:post_slug>", views.EditDraftPost.as_view(), name="edit_draft"),
    path("unpublished", views.UnpublishedPostsView.as_view(), name="unpublished_posts"),
    path("unpublished/set_editor", views.set_editor, name="set_editor"),
    path("unpublished/<slug:post_slug>", views.UnpublishedPostDetailView.as_view(), name="unpublished_post"),
    path("unpublished/edit/<slug:post_slug>", views.EditUnpublishedPost.as_view(), name="edit_post"),
]
