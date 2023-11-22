from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .models import CustomUser


class TypecheckHttpRequest(HttpRequest):
    """Clacc for good typechecking"""

    user: CustomUser | AnonymousUser


class IsAuthorRequiredMixin(PermissionRequiredMixin):
    """Verify that the current user has author permissions."""

    redirect_field_name = "next"
    login_url = reverse_lazy("users:login")
    request: TypecheckHttpRequest

    def has_permission(self) -> bool:
        """Returns True or False depending on the user's status."""
        if self.request.user.is_superuser:
            return True
        if self.request.user.is_anonymous:
            return False
        if not self.request.user.is_author:
            return False
        return True


class IsStaffRequiredMixin(PermissionRequiredMixin):
    """Verify that the current user has staff permissions."""

    redirect_field_name = "next"
    login_url = reverse_lazy("users:login")
    request: TypecheckHttpRequest

    def has_permission(self) -> bool:
        """Returns True or False depending on the user's status."""
        if self.request.user.is_superuser:
            return True
        if self.request.user.is_anonymous:
            return False
        if not self.request.user.is_staff:
            return False
        return True


class IsAuthorDraftRequiredMixin(PermissionRequiredMixin):
    """Verify that the current user has author permissions for current post."""

    redirect_field_name = "next"
    login_url = reverse_lazy("users:login")
    request: TypecheckHttpRequest

    def has_permission(self) -> bool:
        """Returns True or False depending on the user's status."""
        if self.request.user.is_superuser:
            return True
        self.post_instanse = get_object_or_404(self.model, slug=self.kwargs["post_slug"])
        if self.post_instanse.author.id == self.request.user.id:
            return True
        return False
