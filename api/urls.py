"""
api/urls.py
-----------
DRF API routes for the Capstone News app.
"""

from django.urls import path

from . import views

urlpatterns = [
    # Articles
    path(
        "articles/",
        views.ArticleListCreateAPIView.as_view(),
        name="api_article_list_create",
    ),
    path(
        "articles/<int:pk>/",
        views.ArticleDetailAPIView.as_view(),
        name="api_article_detail",
    ),
    path(
        "articles/subscribed/",
        views.SubscribedArticleListAPIView.as_view(),
        name="api_article_subscribed",
    ),

    # Editor approval workflow
    path(
        "articles/pending/",
        views.PendingArticleListAPIView.as_view(),
        name="api_article_pending",
    ),
    path(
        "articles/<int:pk>/approve/",
        views.ApproveArticleAPIView.as_view(),
        name="api_article_approve",
    ),
    path(
        "articles/<int:pk>/reject/",
        views.RejectArticleAPIView.as_view(),
        name="api_article_reject",
    ),

    # Publishers (read-only)
    path(
        "publishers/",
        views.PublisherListAPIView.as_view(),
        name="api_publisher_list",
    ),
    path(
        "publishers/<int:pk>/",
        views.PublisherDetailAPIView.as_view(),
        name="api_publisher_detail",
    ),

    # Publisher subscriptions (reader)
    path(
        "publisher-subscriptions/",
        views.PublisherSubscriptionListCreateAPIView.as_view(),
        name="api_publisher_subscription_list_create",
    ),

    path(
        "publisher-subscriptions/<int:pk>/",
        views.PublisherSubscriptionDeleteAPIView.as_view(),
        name="api_publisher_subscription_delete",
    ),

    # Journalist subscriptions (reader)
    path(
        "journalist-subscriptions/",
        views.JournalistSubscriptionListCreateAPIView.as_view(),
        name="api_journalist_subscription_list_create",
    ),

    path(
        "journalist-subscriptions/<int:pk>/",
        views.JournalistSubscriptionDeleteAPIView.as_view(),
        name="api_journalist_subscription_delete",
    ),

    # Newsletters
    path(
        "newsletters/",
        views.NewsletterListCreateAPIView.as_view(),
        name="api_newsletter_list_create",
    ),
    path(
        "newsletters/<int:pk>/",
        views.NewsletterDetailAPIView.as_view(),
        name="api_newsletter_detail",
    ),
    path(
        "newsletters/<int:pk>/manage/",
        views.NewsletterUpdateDeleteAPIView.as_view(),
        name="api_newsletter_manage",
    ),

    # Publisher memberships (read-only)
    path(
        "publisher-memberships/",
        views.PublisherMembershipListAPIView.as_view(),
        name="api_publisher_membership_list",
    ),
    path(
        "publisher-memberships/<int:pk>/",
        views.PublisherMembershipDetailAPIView.as_view(),
        name="api_publisher_membership_detail",
    ),
]
