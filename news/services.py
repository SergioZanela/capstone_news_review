from __future__ import annotations

from typing import Iterable

from django.conf import settings
from django.core.mail import send_mail

from .models import Article, JournalistSubscription, PublisherSubscription


def _unique_subscriber_emails_for_article(article: Article) -> list[str]:
    """
    Return unique reader email addresses subscribed to this article's publisher
    and/or journalist (author).

    Rules:
    - ignore blank/null emails
    - deduplicate addresses (reader may subscribe to both publisher and
      journalist)
    """
    publisher_emails: Iterable[str] = []
    journalist_emails: Iterable[str] = []

    if getattr(article, "publisher", None) is not None:
        publisher_emails = PublisherSubscription.objects.filter(
            publisher=article.publisher
        ).values_list("reader__email", flat=True)

    if getattr(article, "author", None) is not None:
        journalist_emails = JournalistSubscription.objects.filter(
            journalist=article.author
        ).values_list("reader__email", flat=True)

    emails = {
        (email or "").strip()
        for email in list(publisher_emails) + list(journalist_emails)
    }

    return sorted(email for email in emails if email)


def send_article_approved_email_to_subscribers(article: Article) -> int:
    """
    Send article approval notification emails to subscribed readers.

    Returns:
        int: number of emails attempted/sent (one send_mail call per
            recipient).
    """
    recipient_emails = _unique_subscriber_emails_for_article(article)

    if not recipient_emails:
        return 0

    subject = f"New approved article: {article.title}"

    publisher_name = getattr(article.publisher, "name", "Unknown Publisher")
    author_name = getattr(article.author, "username", "Unknown Author")

    message = (
        f"A new article has been approved and published.\n\n"
        f"Title: {article.title}\n"
        f"Publisher: {publisher_name}\n"
        f"Author: {author_name}\n"
    )

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

    sent_count = 0
    for recipient in recipient_emails:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            # one recipient per email (privacy-safe)
            recipient_list=[recipient],
            fail_silently=False,
        )
        sent_count += 1

    return sent_count
