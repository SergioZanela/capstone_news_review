"""
URL configuration for the Capstone News project.

This module defines routes for the admin site, authentication, web pages,
and API endpoints.
"""

from django.contrib import admin
from django.urls import path, include
from accounts.views import register
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Django built-in authentication routes:
    # /accounts/login/
    # /accounts/logout/
    # /accounts/password_change/ (etc.)
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", register, name="register"),

    # Web UI routes (articles list/detail, approval queue, etc.)
    path("", include("news.urls")),

    # API routes (DRF) - keep this separate from the web UI
    path(
        "api/",
        include("api.urls")
    ),
    path(
        "api-auth/",
        include("rest_framework.urls")
    ),
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]
