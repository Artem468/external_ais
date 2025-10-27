from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from .models import User, Request


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "max_daily_requests",
        "is_active",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Личная информация", {"fields": ("first_name", "last_name", "email")}),
        ("Параметры системы", {"fields": ("params", "max_daily_requests")}),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    formfield_overrides = {
        models.JSONField: {
            "widget": JSONEditorWidget(
                options={
                    "mode": "code",
                    "mainMenuBar": False,
                }
            )
        }
    }

    readonly_fields = ("date_joined", "last_login")


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "updated_at", "parent")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("text", "user__username", "params")
    ordering = ("-created_at",)
    readonly_fields = ("user", "created_at", "updated_at")
    autocomplete_fields = ("parent",)
    formfield_overrides = {
        models.JSONField: {
            "widget": JSONEditorWidget(
                options={
                    "mode": "code",
                    "mainMenuBar": False,
                }
            )
        }
    }

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields + ("status",)
        return self.readonly_fields
