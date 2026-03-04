from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from news.models import (
    Article,
    JournalistSubscription,
    Publisher,
    PublisherSubscription,
)
from news.services import (
    _unique_subscriber_emails_for_article,
    send_article_approved_email_to_subscribers,
)


class ArticleApprovalEmailServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.editor = User.objects.create_user(
            username="editor1",
            email="editor@example.com",
            password="testpass123",
            role="Editor",
        )
        self.journalist = User.objects.create_user(
            username="journalist1",
            email="journalist@example.com",
            password="testpass123",
            role="Journalist",
        )

        self.reader_a = User.objects.create_user(
            username="reader_a",
            email="reader_a@example.com",
            password="testpass123",
            role="Reader",
        )
        self.reader_b = User.objects.create_user(
            username="reader_b",
            email="reader_b@example.com",
            password="testpass123",
            role="Reader",
        )
        self.reader_blank = User.objects.create_user(
            username="reader_blank",
            email="",
            password="testpass123",
            role="Reader",
        )

        self.publisher = Publisher.objects.create(name="Daily Planet")

        self.article = Article.objects.create(
            title="Approved article",
            content="Some content",
            author=self.journalist,
            publisher=self.publisher,
            approved=True,
            approved_by=self.editor,
        )

    def test_unique_subscriber_emails_for_article_deduplicates_and_skips_blanks(  # noqa: E501
        self
    ):
        # reader_a subscribes to publisher
        PublisherSubscription.objects.create(
            reader=self.reader_a,
            publisher=self.publisher,
        )

        # reader_a ALSO subscribes to journalist (duplicate email source)
        JournalistSubscription.objects.create(
            reader=self.reader_a,
            journalist=self.journalist,
        )

        # reader_b subscribes to journalist
        JournalistSubscription.objects.create(
            reader=self.reader_b,
            journalist=self.journalist,
        )

        # blank email user subscribes to publisher (should be ignored)
        PublisherSubscription.objects.create(
            reader=self.reader_blank,
            publisher=self.publisher,
        )

        emails = _unique_subscriber_emails_for_article(self.article)

        self.assertEqual(
            emails,
            sorted(["reader_a@example.com", "reader_b@example.com"]),
        )

    @patch("news.services.send_mail")
    def test_send_article_approved_email_to_subscribers_sends_one_email_per_recipient(  # noqa: E501
        self, mock_send_mail
    ):
        PublisherSubscription.objects.create(
            reader=self.reader_a,
            publisher=self.publisher,
        )
        JournalistSubscription.objects.create(
            reader=self.reader_b,
            journalist=self.journalist,
        )

        sent_count = send_article_approved_email_to_subscribers(self.article)

        self.assertEqual(sent_count, 2)
        self.assertEqual(mock_send_mail.call_count, 2)

        # optional: check recipients called
        called_recipients = sorted(
            call.kwargs["recipient_list"][0]
            for call in mock_send_mail.call_args_list
        )
        self.assertEqual(
            called_recipients,
            ["reader_a@example.com", "reader_b@example.com"],
        )

    @patch("news.services.send_mail")
    def test_send_article_approved_email_to_subscribers_returns_zero_when_no_subscribers(  # noqa: E501
        self, mock_send_mail
    ):
        sent_count = send_article_approved_email_to_subscribers(self.article)

        self.assertEqual(sent_count, 0)
        mock_send_mail.assert_not_called()
