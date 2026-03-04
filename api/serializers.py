from rest_framework import serializers

from news.models import (
    Article,
    JournalistSubscription,
    Newsletter,
    Publisher,
    PublisherSubscription,
    PublisherMembership,
)

from accounts.models import CustomUser


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Public/article-list serializer.
    Keeps the response small for list endpoints.
    """

    author_username = serializers.CharField(
        source="author.username", read_only=True
    )
    publisher_name = serializers.CharField(
        source="publisher.name", read_only=True, default=None
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "author",
            "author_username",
            "publisher",
            "publisher_name",
            "approved",
            "created_at",
            "approved_at",
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Article detail serializer.
    Includes full content and approval metadata.
    """

    author_username = serializers.CharField(
        source="author.username", read_only=True
    )
    approved_by_username = serializers.CharField(
        source="approved_by.username", read_only=True, default=None
    )
    publisher_name = serializers.CharField(
        source="publisher.name", read_only=True, default=None
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_username",
            "publisher",
            "publisher_name",
            "approved",
            "created_at",
            "approved_at",
            "approved_by",
            "approved_by_username",
        ]
        read_only_fields = [
            "author",
            "approved",
            "created_at",
            "approved_at",
            "approved_by",
        ]


class ArticleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used when journalists submit new articles.

    We do NOT expose author/approved fields to the client:
    - author is set from request.user
    - approved is forced to False in the view
    """

    class Meta:
        model = Article
        fields = ["title", "content", "publisher"]


class PublisherSerializer(serializers.ModelSerializer):
    """
    Read-only publisher serializer.
    """
    class Meta:
        model = Publisher
        fields = ["id", "name", "description", "created_at"]


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Safe read-only user serializer for API responses.
    Includes basic identity and role fields only.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role"]
        read_only_fields = ["id", "username", "email", "role"]


class PublisherSubscriptionSerializer(serializers.ModelSerializer):
    """
    Reader subscription to a publisher.

    POST input:
    - publisher

    Read output:
    - includes publisher name and reader username for convenience
    """
    publisher_name = serializers.CharField(
        source="publisher.name", read_only=True
    )
    reader_username = serializers.CharField(
        source="reader.username", read_only=True
    )

    class Meta:
        model = PublisherSubscription
        fields = [
            "id",
            "publisher",
            "publisher_name",
            "reader",
            "reader_username",
            "created_at",
        ]
        read_only_fields = ["reader", "reader_username", "created_at"]


class JournalistSubscriptionSerializer(serializers.ModelSerializer):
    """
    Reader subscription to a journalist.

    POST input:
    - journalist

    Read output:
    - includes usernames for convenience
    """
    journalist_username = serializers.CharField(
        source="journalist.username", read_only=True
    )
    reader_username = serializers.CharField(
        source="reader.username", read_only=True
    )

    class Meta:
        model = JournalistSubscription
        fields = [
            "id",
            "journalist",
            "journalist_username",
            "reader",
            "reader_username",
            "created_at",
        ]
        read_only_fields = ["reader", "reader_username", "created_at"]


class NewsletterListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for newsletter list endpoint.
    """
    author_username = serializers.CharField(
        source="author.username", read_only=True
    )
    article_count = serializers.IntegerField(
        source="articles.count", read_only=True
    )

    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "description",
            "author_username",
            "article_count",
            "created_at",
        ]


class NewsletterDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a newsletter, including linked article IDs.
    """
    author_username = serializers.CharField(
        source="author.username", read_only=True
    )
    articles = ArticleListSerializer(many=True, read_only=True)

    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "description",
            "author",
            "author_username",
            "articles",
            "created_at",
        ]
        read_only_fields = ["author", "created_at"]


class NewsletterCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Create/update serializer for newsletters.

    Allows setting article IDs (many-to-many).
    Author is set from request.user in the view.
    """
    articles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Article.objects.all(),
        required=False,
    )

    class Meta:
        model = Newsletter
        fields = ["title", "description", "articles"]


class PublisherMembershipSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for publisher memberships.

    Shows which user belongs to which publisher and their membership role
    (editor/journalist within that publisher).
    """
    publisher_name = serializers.CharField(
        source="publisher.name", read_only=True
    )
    user_username = serializers.CharField(
        source="user.username", read_only=True
    )

    class Meta:
        model = PublisherMembership
        fields = [
            "id",
            "publisher",
            "publisher_name",
            "user",
            "user_username",
            "member_role",
        ]
