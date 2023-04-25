from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path("register", views.RegisterUser.as_view(), name="register"),
    path("login", views.LoginUser.as_view(), name="login"),
    path("logout", views.LogoutView.as_view(next_page=reverse_lazy("login")), name="logout"),
]
