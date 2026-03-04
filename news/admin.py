"""
news/admin.py

Admin registrations for news models.
"""

from django.contrib import admin

from .models import (
    Article,
    JournalistSubscription,
    Newsletter,
    Publisher,
    PublisherMembership,
    PublisherSubscription,
)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(PublisherMembership)
class PublisherMembershipAdmin(admin.ModelAdmin):
    list_display = ("publisher", "user", "member_role")
    list_filter = ("member_role", "publisher")
    search_fields = ("publisher__name", "user__username", "user__email")
    autocomplete_fields = ("publisher", "user")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher", "approved", "created_at")
    list_filter = ("approved", "publisher", "created_at")
    search_fields = ("title", "content")
    autocomplete_fields = ("author", "publisher", "approved_by")


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at")
    search_fields = ("title", "description")
    autocomplete_fields = ("author",)
    filter_horizontal = ("articles",)


@admin.register(PublisherSubscription)
class PublisherSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("reader", "publisher", "created_at")
    list_filter = ("publisher",)
    search_fields = ("reader__username", "reader__email", "publisher__name")
    autocomplete_fields = ("reader", "publisher")


@admin.register(JournalistSubscription)
class JournalistSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("reader", "journalist", "created_at")
    list_filter = ("journalist",)
    search_fields = (
        "reader__username",
        "reader__email",
        "journalist__username",
        "journalist__email",
    )
    autocomplete_fields = ("reader", "journalist")
