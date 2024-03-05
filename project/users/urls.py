from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from . import views

app_name = "users"
urlpatterns = [
    path("register", views.RegisterUser.as_view(), name="register"),
    path(
        "activate/mail",
        TemplateView.as_view(template_name="users/activation_mail_sended.html"),
        name="activation_mail_sended",
    ),
    path("activate/<str:sign>", views.user_activate, name="register_activate"),
    path("login", views.LoginUser.as_view(), name="login"),
    path("logout", views.LogoutView.as_view(next_page=reverse_lazy("users:login")), name="logout"),
    path("author/<str:username>", views.AuthorPosts.as_view(), name="author_posts"),
    path("profile", views.EditProfileUser.as_view(), name="profile_edit"),
    path("subscribe/<str:author_username>", views.subscribe, name="subscribe"),
]
