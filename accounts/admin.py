"""
accounts/admin.py

Admin configuration for the custom user model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


def approve_users(modeladmin, request, queryset):
    updated = queryset.filter(is_active=False).update(is_active=True)
    modeladmin.message_user(request, f"Approved {updated} user(s).")


approve_users.short_description = (  # type: ignore[attr-defined]
    "Approve selected users (activate)"
)


class CustomUserCreationForm(UserCreationForm):
    """
    Admin form for creating users and selecting a role.
    """

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role")


class CustomUserChangeForm(UserChangeForm):
    """
    Admin form for updating users.
    """

    class Meta:
        model = CustomUser
        fields = "__all__"


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for CustomUser.
    """

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    actions = [approve_users]
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )  # type: ignore[assignment]

    add_fieldsets = (  # type: ignore[assignment]
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")
