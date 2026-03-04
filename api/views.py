from typing import Any

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from news.models import (
    Article,
    JournalistSubscription,
    Newsletter,
    Publisher,
    PublisherMembership,
    PublisherSubscription,
)

from news.services import send_article_approved_email_to_subscribers

from .permissions import (
    CanReadApprovedArticles,
    IsEditor,
    IsJournalist,
    IsJournalistOrEditor,
    IsOwnerOrEditor,
    IsOwnerOrEditorForNewsletter,
    IsReader,
)

from .serializers import (
    ArticleCreateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    JournalistSubscriptionSerializer,
    NewsletterCreateUpdateSerializer,
    NewsletterDetailSerializer,
    NewsletterListSerializer,
    PublisherMembershipSerializer,
    PublisherSerializer,
    PublisherSubscriptionSerializer,
)


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    """
    GET:
      - Authenticated users can list approved articles only.

    POST:
      - Journalists can submit new articles.
      - author is automatically set from request.user
      - approved is forced to False
    """

    def get_queryset(self) -> Any:  # type: ignore[override]
        user = self.request.user

        # Anonymous users: no access (keep your current behavior)
        if not user or not user.is_authenticated:
            return Article.objects.none()

        role = (getattr(user, "role", "") or "").strip().lower()

        # Editors can see all articles (approved + pending)
        if role == "editor":
            qs = Article.objects.all()

        # Journalists can see approved articles + their own pending articles
        elif role == "journalist":
            qs = (
                Article.objects.filter(approved=True)
                | Article.objects.filter(author=user)
            )

        # Readers: approved only
        else:
            qs = Article.objects.filter(approved=True)

        # Optional filters:
        #   /api/articles/?publisher=1
        #   /api/articles/?author=2
        publisher_id = self.request.GET.get("publisher")
        author_id = self.request.GET.get("author")

        if publisher_id:
            qs = qs.filter(publisher_id=publisher_id)

        if author_id:
            qs = qs.filter(author_id=author_id)

        return qs.distinct().order_by("-created_at")

    def get_serializer_class(self) -> Any:  # type: ignore[override]
        if self.request.method == "POST":
            return ArticleCreateSerializer
        return ArticleListSerializer

    def get_permissions(self) -> list[Any]:  # type: ignore[override]
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsJournalist()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer: Any) -> None:
        serializer.save(
            author=self.request.user,
            approved=False,
            approved_at=None,
            approved_by=None,
        )


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/update/delete a single article.

    GET:
    - Approved articles: any authenticated user
    - Unapproved articles: editors only

    PUT/PATCH/DELETE:
    - Owner journalist or editor only
    """

    queryset = Article.objects.select_related(
        "author", "publisher", "approved_by"
    )
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> Any:  # type: ignore[override]
        if self.request.method in {"PUT", "PATCH"}:
            return ArticleCreateSerializer
        return ArticleDetailSerializer

    def get_permissions(self) -> list[Any]:  # type: ignore[override]
        if self.request.method in {"PUT", "PATCH", "DELETE"}:
            return [permissions.IsAuthenticated(), IsOwnerOrEditor()]
        return [permissions.IsAuthenticated(), CanReadApprovedArticles()]

    def get_object(self) -> Any:  # type: ignore[override]
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class PendingArticleListAPIView(generics.ListAPIView):
    """
    Editor-only list of pending articles (approved=False).
    """
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditor]

    def get_queryset(self) -> Any:  # type: ignore[override]
        return Article.objects.filter(approved=False).order_by("-created_at")


class SubscribedArticleListAPIView(generics.ListAPIView):
    """
    Returns approved articles from the authenticated reader's subscribed
    publishers and subscribed journalists.
    """

    serializer_class = ArticleListSerializer
    permission_classes = [permissions.IsAuthenticated, IsReader]

    def get_queryset(self) -> Any:
        user = self.request.user

        publisher_ids = PublisherSubscription.objects.filter(
            reader=user
        ).values_list("publisher_id", flat=True)

        journalist_ids = JournalistSubscription.objects.filter(
            reader=user
        ).values_list("journalist_id", flat=True)

        qs = Article.objects.filter(approved=True).filter(
            Q(publisher_id__in=publisher_ids) | Q(author_id__in=journalist_ids)
        )

        return qs.distinct().order_by("-created_at")


class ApproveArticleAPIView(APIView):
    """
    Editor-only action endpoint to approve an article.
    """
    permission_classes = [permissions.IsAuthenticated, IsEditor]

    def post(self, request: Any, pk: int) -> Response:
        article = get_object_or_404(Article, pk=pk)

        article.approved = True
        article.approved_at = timezone.now()
        article.approved_by = request.user
        article.save(update_fields=["approved", "approved_at", "approved_by"])

        # Notify subscribed readers after approval
        send_article_approved_email_to_subscribers(article)

        return Response(
            {
                "message": "Article approved.",
                "article_id": article.pk,
                "approved": article.approved,
                "approved_at": article.approved_at,
                "approved_by": request.user.username,
            },
            status=status.HTTP_200_OK,
        )


class RejectArticleAPIView(APIView):
    """
    Editor-only action endpoint to reject an article.

    Current behavior: delete article (simple version).
    """
    permission_classes = [permissions.IsAuthenticated, IsEditor]

    def post(self, request: Any, pk: int) -> Response:
        article = get_object_or_404(Article, pk=pk)
        article_id = article.pk
        article.delete()

        return Response(
            {
                "message": "Article rejected and deleted.",
                "article_id": article_id,
            },
            status=status.HTTP_200_OK,
        )


class PublisherListAPIView(generics.ListAPIView):
    """
    List all publishers (authenticated users).
    """
    queryset = Publisher.objects.all().order_by("name")
    serializer_class = PublisherSerializer
    permission_classes = [permissions.IsAuthenticated]


class PublisherDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a single publisher (authenticated users).
    """
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [permissions.IsAuthenticated]


class PublisherSubscriptionListCreateAPIView(generics.ListCreateAPIView):
    """
    Reader subscription endpoint for publishers.

    GET:
    - readers see only their own publisher subscriptions

    POST:
    - readers subscribe to a publisher
    - reader is set automatically from request.user
    """
    serializer_class = PublisherSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsReader]

    def get_queryset(self) -> Any:  # type: ignore[override]
        return (
            PublisherSubscription.objects
            .filter(reader=self.request.user)
            .select_related("publisher", "reader")
            .order_by("-created_at")
        )

    def perform_create(self, serializer: Any) -> None:
        serializer.save(reader=self.request.user)


class PublisherSubscriptionDeleteAPIView(generics.DestroyAPIView):
    """
    Reader unsubscribe endpoint for publisher subscriptions.

    Readers can only delete their own subscriptions.
    Editors may delete any (fallback for admin/testing).
    """
    queryset = PublisherSubscription.objects.select_related(
        "publisher", "reader"
    )
    serializer_class = PublisherSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrEditor]

    def get_object(self) -> Any:  # type: ignore[override]
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class JournalistSubscriptionListCreateAPIView(generics.ListCreateAPIView):
    """
    Reader subscription endpoint for journalists.

    GET:
    - readers see only their own journalist subscriptions

    POST:
    - readers subscribe to a journalist
    - reader is set automatically from request.user
    """
    serializer_class = JournalistSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsReader]

    def get_queryset(self) -> Any:  # type: ignore[override]
        return (
            JournalistSubscription.objects
            .filter(reader=self.request.user)
            .select_related("journalist", "reader")
            .order_by("-created_at")
        )

    def perform_create(self, serializer: Any) -> None:
        serializer.save(reader=self.request.user)


class JournalistSubscriptionDeleteAPIView(generics.DestroyAPIView):
    """
    Reader unsubscribe endpoint for journalist subscriptions.

    Readers can only delete their own subscriptions.
    Editors may delete any (fallback for admin/testing).
    """
    queryset = JournalistSubscription.objects.select_related(
        "journalist", "reader"
    )
    serializer_class = JournalistSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrEditor]

    def get_object(self) -> Any:  # type: ignore[override]
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class NewsletterListCreateAPIView(generics.ListCreateAPIView):
    """
    Newsletters endpoint.

    GET:
    - any authenticated user can list newsletters

    POST:
    - journalists and editors can create newsletters
    - author is set automatically from request.user
    """
    queryset = (
        Newsletter.objects
        .select_related("author")
        .prefetch_related("articles")
        .order_by("-created_at")
    )
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> Any:  # type: ignore[override]
        if self.request.method == "POST":
            return NewsletterCreateUpdateSerializer
        return NewsletterListSerializer

    def get_permissions(self) -> list[Any]:  # type: ignore[override]
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsJournalistOrEditor()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer: Any) -> None:
        serializer.save(author=self.request.user)


class NewsletterDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/update/delete a newsletter.

    GET:
    - authenticated users can view (subject to your existing permissions)

    PUT/PATCH/DELETE:
    - owner journalist or editor only
    """

    queryset = (
        Newsletter.objects
        .prefetch_related("articles")
        .select_related("author")
    )

    def get_serializer_class(self) -> Any:  # type: ignore[override]
        if self.request.method in {"PUT", "PATCH"}:
            return NewsletterCreateUpdateSerializer
        return NewsletterDetailSerializer

    def get_permissions(self) -> list[Any]:  # type: ignore[override]
        if self.request.method in {"PUT", "PATCH", "DELETE"}:
            return [
                permissions.IsAuthenticated(),
                IsOwnerOrEditorForNewsletter(),
            ]
        return [permissions.IsAuthenticated()]

    def get_object(self) -> Any:  # type: ignore[override]
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class NewsletterUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Update/delete a newsletter.

    Rules:
    - Author can update/delete own newsletter
    - Editors can update/delete any newsletter
    """
    queryset = (
        Newsletter.objects
        .select_related("author")
        .prefetch_related("articles")
    )
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrEditorForNewsletter,
    ]

    def get_serializer_class(self) -> Any:  # type: ignore[override]
        if self.request.method in {"PUT", "PATCH"}:
            return NewsletterCreateUpdateSerializer
        return NewsletterDetailSerializer

    def get_object(self) -> Any:  # type: ignore[override]
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class PublisherMembershipListAPIView(generics.ListAPIView):
    """
    List publisher memberships (authenticated users).

    Optional filters:
    - /api/publisher-memberships/?publisher=<id>
    - /api/publisher-memberships/?user=<id>
    - /api/publisher-memberships/?member_role=editor
    """
    serializer_class = PublisherMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:  # type: ignore[override]
        qs = (
            PublisherMembership.objects
            .select_related("publisher", "user")
            .order_by("publisher__name", "user__username")
        )

        # Use request.GET to avoid Pylance warning on query_params
        publisher_id = self.request.GET.get("publisher")
        user_id = self.request.GET.get("user")
        member_role = self.request.GET.get("member_role")

        if publisher_id:
            qs = qs.filter(publisher_id=publisher_id)

        if user_id:
            qs = qs.filter(user_id=user_id)

        if member_role:
            qs = qs.filter(member_role__iexact=member_role)

        return qs


class PublisherMembershipDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a single publisher membership (authenticated users).
    """
    queryset = PublisherMembership.objects.select_related("publisher", "user")
    serializer_class = PublisherMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
