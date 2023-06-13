from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


class IsAuthorRequiredMixin(PermissionRequiredMixin):
    redirect_field_name = "next"
    login_url = reverse_lazy("login")

    def has_permission(self):
        if self.request.user.is_superuser:
            return True
        if self.request.user.is_anonymous or not self.request.user.is_author:
            return False
        return True


class IsStaffRequiredMixin(PermissionRequiredMixin):
    redirect_field_name = "next"
    login_url = reverse_lazy("login")

    def has_permission(self):
        if self.request.user.is_superuser:
            return True
        if self.request.user.is_anonymous or not self.request.user.is_staff:
            return False
        return True


class IsAuthorDraftRequiredMixin(PermissionRequiredMixin):
    redirect_field_name = "next"
    login_url = reverse_lazy("login")

    def has_permission(self):
        if self.request.user.is_superuser:
            return True
        self.post_instanse = get_object_or_404(self.model, slug=self.kwargs["post_slug"])
        if self.post_instanse.author.id == self.request.user.id:
            return True
        return False
