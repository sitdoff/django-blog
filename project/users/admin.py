from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


# Register your models here.
class CustomUserAdmin(UserAdmin):
    empty_value_display = "Пусто"
    readonly_fields = ("date_joined", "last_login")
    list_display = (
        "username",
        "first_name",
        "email",
        "is_author",
        "is_staff",
        "is_superuser",
        "is_active",
        "is_banned",
    )
    search_fields = ("username", "first_name", "email")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_author")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Personal info"), {"fields": ("photo", "first_name", "email", "bio", "subscriptions")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_author",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "is_banned",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    class Meta:
        verbose_name = "Пользователя"
        verbose_name_plural = "Пользователи"


admin.site.register(CustomUser, CustomUserAdmin)
