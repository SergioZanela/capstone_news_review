"""
news/models.py

Database models for:
- Publisher
- PublisherMembership (links users to publishers with a role
  inside that publisher)
- Article
- Newsletter
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Publisher(models.Model):
    """
    Represents a publisher. Editors and Journalists are linked via
    PublisherMembership.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class PublisherMembership(models.Model):
    """
    Links a user to a publisher with a membership type (Editor or Journalist).

    This avoids circular migration dependencies between accounts and news.
    """

    MEMBER_EDITOR = "Editor"
    MEMBER_JOURNALIST = "Journalist"

    MEMBER_ROLE_CHOICES = (
        (MEMBER_EDITOR, "Editor"),
        (MEMBER_JOURNALIST, "Journalist"),
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="publisher_memberships",
    )
    member_role = models.CharField(max_length=20, choices=MEMBER_ROLE_CHOICES)

    class Meta:
        unique_together = ("publisher", "user", "member_role")

    def clean(self):
        super().clean()
        if getattr(self.user, "role", None) not in {"Editor", "Journalist"}:
            raise ValidationError(
                "Only Editor/Journalist users can be members of a publisher."
            )

        user_role = getattr(self.user, "role", None)
        if self.member_role == self.MEMBER_EDITOR and user_role != "Editor":
            raise ValidationError(
                "This membership role requires the user to have the "
                "Editor role."
            )

        if (
            self.member_role == self.MEMBER_JOURNALIST
            and user_role != "Journalist"
        ):
            raise ValidationError(
                "This membership role requires the user to have the "
                "Journalist role."
            )

    def __str__(self) -> str:
        return (
            f"{self.publisher.name} - {self.user.username} "
            f"({self.member_role})"
        )


class Article(models.Model):
    """
    Article content written by a Journalist.

    An article can be:
    - independent (publisher is null)
    - publisher content (publisher is set)
    """

    title = models.CharField(max_length=255)
    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="articles_authored",
        limit_choices_to=Q(role__iexact="Journalist"),
    )
    author_id: int | None

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        help_text=(
            "Set for publisher content; leave blank for independent "
            "articles."
        ),
    )

    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles_approved",
        limit_choices_to=Q(role__iexact="Editor"),
    )

    def clean(self):
        """
        Model-level validation for Article.

        Why this guard exists:
        - Django admin runs full_clean() before saving.
        - If 'author' is not chosen yet, accessing self.author can raise
          RelatedObjectDoesNotExist ("Article has no author").
        - So we first check author_id (safe FK id) before reading
          self.author.role.
        """
        super().clean()

        # If author is missing, raise a normal validation error instead
        # of crashing.
        if not self.author_id:
            raise ValidationError(
                {
                    "author": (
                        "Please select an author (Journalist)."
                    )
                }
            )

        # Enforce: only Journalist users can be authors.
        if getattr(self.author, "role", None) != "Journalist":
            raise ValidationError(
                {
                    "author": (
                        "Only Journalist users can be authors of articles."
                    )
                }
            )

    def __str__(self) -> str:
        return self.title


class Newsletter(models.Model):
    """
    Newsletter that groups multiple articles together.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="newsletters_authored",
        limit_choices_to=(
            Q(role__iexact="Journalist") | Q(role__iexact="Editor")
        ),
    )

    articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name="newsletters",
    )

    def __str__(self) -> str:
        return self.title


class PublisherSubscription(models.Model):
    """
    A reader subscribing to a publisher.
    """

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    reader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="publisher_subscriptions",
        limit_choices_to=Q(role__iexact="Reader"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("publisher", "reader")

    def clean(self):
        super().clean()
        if getattr(self.reader, "role", None) != "Reader":
            raise ValidationError(
                "Only users with the Reader role can subscribe to "
                "publishers."
            )

    def __str__(self) -> str:
        return f"{self.reader.username} -> {self.publisher.name}"


class JournalistSubscription(models.Model):
    """
    A reader subscribing to an independent Journalist   .
    """

    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="journalist_subscribers",
        limit_choices_to=Q(role__iexact="Journalist"),
    )
    reader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="journalist_subscriptions",
        limit_choices_to=Q(role__iexact="Reader"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("journalist", "reader")

    def clean(self):
        super().clean()
        if getattr(self.reader, "role", None) != "Reader":
            raise ValidationError(
                "Only users with the Reader role can subscribe to "
                "Journalists."
            )
        if getattr(self.journalist, "role", None) != "Journalist":
            raise ValidationError(
                "Subscriptions can only target Journalist users."
            )

    def __str__(self) -> str:
        return f"{self.reader.username} -> {self.journalist.username}"
