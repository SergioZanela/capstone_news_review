from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from accounts.models import CustomUser
from news.models import (
    Article,
    JournalistSubscription,
    Newsletter,
    Publisher,
    PublisherSubscription,
)


class ArticleAPITests(APITestCase):
    def setUp(self):
        # Users (roles must match your DB choices exactly)
        self.reader = CustomUser.objects.create_user(
            username="reader1",
            password="TestPass123!",
            role="Reader",
        )
        self.journalist = CustomUser.objects.create_user(
            username="journalist1",
            password="TestPass123!",
            role="Journalist",
        )
        self.editor = CustomUser.objects.create_user(
            username="editor1",
            password="TestPass123!",
            role="Editor",
        )

        # Existing articles
        self.approved_article = Article.objects.create(
            title="Approved Article",
            content="Approved content",
            author=self.journalist,
            approved=True,
            approved_by=self.editor,
        )
        self.pending_article = Article.objects.create(
            title="Pending Article",
            content="Pending content",
            author=self.journalist,
            approved=False,
        )
        # Additional users/content for subscribed feed tests
        self.other_journalist = CustomUser.objects.create_user(
            username="journalist2",
            password="TestPass123!",
            role="Journalist",
        )

        self.publisher = Publisher.objects.create(name="Daily Planet")
        self.other_publisher = Publisher.objects.create(name="Other News")

        self.subscribed_publisher_article = Article.objects.create(
            title="Subscribed Publisher Article",
            content="From subscribed publisher",
            author=self.editor,  # author can be any user your model allows
            publisher=self.publisher,
            approved=True,
            approved_by=self.editor,
        )

        self.subscribed_journalist_article = Article.objects.create(
            title="Subscribed Journalist Article",
            content="From subscribed journalist",
            author=self.other_journalist,
            approved=True,
            approved_by=self.editor,
        )

        self.unsubscribed_article = Article.objects.create(
            title="Unsubscribed Article",
            content="Should not appear",
            author=self.editor,
            publisher=self.other_publisher,
            approved=True,
            approved_by=self.editor,
        )

        self.pending_subscribed_article = Article.objects.create(
            title="Pending Subscribed Article",
            content="Subscribed source but pending",
            author=self.other_journalist,
            approved=False,
        )

        PublisherSubscription.objects.create(
            reader=self.reader, publisher=self.publisher
        )
        JournalistSubscription.objects.create(
            reader=self.reader, journalist=self.other_journalist
        )

        self.article_list_url = reverse("api_article_list_create")
        self.article_detail_url = reverse(
            "api_article_detail", args=[self.approved_article.pk]
        )
        self.pending_article_detail_url = reverse(
            "api_article_detail", args=[self.pending_article.pk]
        )
        self.article_subscribed_url = reverse("api_article_subscribed")

    def test_editor_can_delete_article_via_detail_endpoint(self):
        self.client.login(username="editor1", password="TestPass123!")

        article = Article.objects.create(
            title="Delete Me",
            content="To be deleted by editor",
            author=self.journalist,
            approved=True,
            approved_by=self.editor,
        )
        detail_url = reverse("api_article_detail", args=[article.pk])

        response = self.client.delete(detail_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK],
        )
        self.assertFalse(Article.objects.filter(pk=article.pk).exists())

    def test_reader_cannot_delete_article_via_detail_endpoint(self):
        self.client.login(username="reader1", password="TestPass123!")

        article = Article.objects.create(
            title="Reader Cannot Delete",
            content="Should remain",
            author=self.journalist,
            approved=True,
            approved_by=self.editor,
        )
        detail_url = reverse("api_article_detail", args=[article.pk])

        response = self.client.delete(detail_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )
        self.assertTrue(Article.objects.filter(pk=article.pk).exists())

    def test_reader_subscribed_returns_approved_articles(self):
        self.client.login(username="reader1", password="TestPass123!")

        response = self.client.get(self.article_subscribed_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = getattr(response, "data", None)
        self.assertIsNotNone(response_data)

        if isinstance(response_data, dict):
            data = response_data.get("results", response_data)
        else:
            data = response_data

        returned_titles = {item["title"] for item in data} if data else set()

        self.assertIn("Subscribed Publisher Article", returned_titles)
        self.assertIn("Subscribed Journalist Article", returned_titles)

        self.assertNotIn("Unsubscribed Article", returned_titles)
        self.assertNotIn("Pending Subscribed Article", returned_titles)

    def test_reader_can_list_articles(self):
        self.client.login(username="reader1", password="TestPass123!")

        response = self.client.get(self.article_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reader_cannot_create_article(self):
        self.client.login(username="reader1", password="TestPass123!")

        payload = {
            "title": "Reader Should Not Create",
            "content": "This should be blocked.",
        }

        response = self.client.post(
            self.article_list_url, payload, format="json"
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )

    def test_journalist_can_create_article(self):
        self.client.login(username="journalist1", password="TestPass123!")

        payload = {
            "title": "Journalist Draft",
            "content": "Article submitted by journalist.",
        }

        response = self.client.post(
            self.article_list_url, payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Article.objects.filter(title="Journalist Draft").exists()
        )

    def test_reader_list_excludes_pending_articles(self):
        self.client.login(username="reader1", password="TestPass123!")

        response = self.client.get(self.article_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = getattr(response, "data", None)
        self.assertIsNotNone(response_data)

        # Works for paginated and non-paginated DRF responses
        if isinstance(response_data, dict):
            data = response_data.get("results", response_data)
        else:
            data = response_data

        self.assertIsNotNone(data)
        returned_titles = (
            {item["title"] for item in data} if data else set()
        )
        self.assertIn("Approved Article", returned_titles)
        self.assertNotIn("Pending Article", returned_titles)

    def test_journalist_can_patch_own_article_via_detail_endpoint(self):
        self.client.login(username="journalist1", password="TestPass123!")

        article = Article.objects.create(
            title="Original Title",
            content="Original content",
            author=self.journalist,
            approved=False,
        )
        detail_url = reverse("api_article_detail", args=[article.pk])

        response = self.client.patch(
            detail_url,
            {"title": "Updated Title"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        article.refresh_from_db()
        self.assertEqual(article.title, "Updated Title")

    def test_editor_list_includes_pending_articles(self):
        self.client.login(username="editor1", password="TestPass123!")

        response = self.client.get(self.article_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = getattr(response, "data", None)
        self.assertIsNotNone(response_data)

        if isinstance(response_data, dict):
            data = response_data.get("results", response_data)
        else:
            data = response_data

        returned_titles = (
            {item["title"] for item in data} if data else set()
        )
        self.assertIn("Approved Article", returned_titles)
        self.assertIn("Pending Article", returned_titles)

    def test_journalist_list_includes_own_pending_articles(self):
        self.client.login(username="journalist1", password="TestPass123!")

        response = self.client.get(self.article_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = getattr(response, "data", None)
        self.assertIsNotNone(response_data)

        if isinstance(response_data, dict):
            data = response_data.get("results", response_data)
        else:
            data = response_data

        returned_titles = (
            {item["title"] for item in data} if data else set()
        )
        self.assertIn("Approved Article", returned_titles)
        self.assertIn("Pending Article", returned_titles)

    def test_reader_cannot_access_pending_article_detail(self):
        self.client.login(username="reader1", password="TestPass123!")

        response = self.client.get(self.pending_article_detail_url)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND,
            ],
        )

    def test_editor_can_access_pending_article_detail(self):
        self.client.login(username="editor1", password="TestPass123!")

        response = self.client.get(self.pending_article_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = getattr(response, "data", None)
        self.assertIsNotNone(response_data)

        if isinstance(response_data, dict):
            self.assertEqual(response_data.get("title"), "Pending Article")

    def test_editor_can_approve_pending_article(self):
        self.client.login(username="editor1", password="TestPass123!")

        approve_url = reverse(
            "api_article_approve", args=[self.pending_article.pk]
        )

        response = self.client.post(approve_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT],
        )

        self.pending_article.refresh_from_db()
        self.assertTrue(self.pending_article.approved)
        self.assertEqual(self.pending_article.approved_by, self.editor)

    def test_reader_cannot_approve_pending_article(self):
        self.client.login(username="reader1", password="TestPass123!")

        approve_url = reverse(
            "api_article_approve", args=[self.pending_article.pk]
        )

        response = self.client.post(approve_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )

        self.pending_article.refresh_from_db()
        self.assertFalse(self.pending_article.approved)
        self.assertIsNone(self.pending_article.approved_by)

    def test_journalist_cannot_approve_pending_article(self):
        self.client.login(username="journalist1", password="TestPass123!")

        approve_url = reverse(
            "api_article_approve", args=[self.pending_article.pk]
        )

        response = self.client.post(approve_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )

        self.pending_article.refresh_from_db()
        self.assertFalse(self.pending_article.approved)
        self.assertIsNone(self.pending_article.approved_by)

    def test_editor_can_reject_pending_article(self):
        self.client.login(username="editor1", password="TestPass123!")

        reject_url = reverse(
            "api_article_reject", args=[self.pending_article.pk]
        )

        response = self.client.post(reject_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT],
        )

        # The exact post-reject behavior can vary by implementation:
        # - delete the article
        # - keep it and mark rejected
        # We'll assert the pending article is no longer pending/visible
        # as pending.
        exists = Article.objects.filter(pk=self.pending_article.pk).exists()

        if exists:
            self.pending_article.refresh_from_db()
            # If you keep rejected articles, at minimum it should
            # not become approved
            self.assertFalse(self.pending_article.approved)
        else:
            self.assertFalse(exists)

    def test_reader_cannot_reject_pending_article(self):
        self.client.login(username="reader1", password="TestPass123!")

        reject_url = reverse(
            "api_article_reject", args=[self.pending_article.pk]
        )

        response = self.client.post(reject_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )

        # Ensure article was not modified/deleted by unauthorized user
        self.assertTrue(
            Article.objects.filter(pk=self.pending_article.pk).exists()
        )
        self.pending_article.refresh_from_db()
        self.assertFalse(self.pending_article.approved)
        self.assertIsNone(self.pending_article.approved_by)

    def test_reader_cannot_access_pending_articles_endpoint(self):
        self.client.login(username="reader1", password="TestPass123!")

        pending_url = reverse("api_article_pending")

        response = self.client.get(pending_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )

    def test_reader_cannot_patch_article_via_detail_endpoint(self):
        self.client.login(username="reader1", password="TestPass123!")

        article = Article.objects.create(
            title="Reader Cannot Patch",
            content="Should not change",
            author=self.journalist,
            approved=True,
            approved_by=self.editor,
        )
        detail_url = reverse("api_article_detail", args=[article.pk])

        response = self.client.patch(
            detail_url,
            {"title": "Hacked Title"},
            format="json",
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )

        article.refresh_from_db()
        self.assertEqual(article.title, "Reader Cannot Patch")

    def test_reader_can_list_newsletters(self):
        self.client.login(username="reader1", password="TestPass123!")

        newsletter = Newsletter.objects.create(
            title="Morning Brief",
            description="Top stories for today",
            author=self.journalist,
        )
        newsletter.articles.add(self.approved_article)

        url = reverse("api_newsletter_list_create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = getattr(response, "data", None)
        self.assertIsNotNone(response_data)

        if isinstance(response_data, dict):
            data = response_data.get("results", response_data)
        else:
            data = response_data

        titles = {item["title"] for item in data} if data else set()
        self.assertIn("Morning Brief", titles)

    def test_reader_cannot_create_newsletter(self):
        self.client.login(username="reader1", password="TestPass123!")

        url = reverse("api_newsletter_list_create")
        payload = {
            "title": "Reader Newsletter",
            "description": "Should not be allowed",
            "article_ids": [self.approved_article.pk],
        }

        response = self.client.post(url, payload, format="json")

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )
        self.assertFalse(
            Newsletter.objects.filter(
                title="Reader Newsletter"
            ).exists()
        )

    def test_journalist_can_create_newsletter(self):
        self.client.login(username="journalist1", password="TestPass123!")

        url = reverse("api_newsletter_list_create")
        payload = {
            "title": "Journalist Newsletter",
            "description": "Created by journalist",
            "article_ids": [self.approved_article.pk],
        }

        response = self.client.post(url, payload, format="json")

        self.assertIn(
            response.status_code,
            [status.HTTP_201_CREATED, status.HTTP_200_OK],
        )
        self.assertTrue(
            Newsletter.objects.filter(
                title="Journalist Newsletter"
            ).exists()
        )

    def test_editor_can_delete_newsletter(self):
        self.client.login(username="editor1", password="TestPass123!")

        newsletter = Newsletter.objects.create(
            title="Delete Newsletter",
            description="To be deleted by editor",
            author=self.journalist,
        )
        newsletter.articles.add(self.approved_article)

        detail_url = reverse("api_newsletter_detail", args=[newsletter.pk])

        response = self.client.delete(detail_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK],
        )
        self.assertFalse(Newsletter.objects.filter(pk=newsletter.pk).exists())

    def test_reader_cannot_delete_newsletter(self):
        self.client.login(username="reader1", password="TestPass123!")

        newsletter = Newsletter.objects.create(
            title="Reader Cannot Delete Newsletter",
            description="Should remain",
            author=self.journalist,
        )
        newsletter.articles.add(self.approved_article)

        detail_url = reverse("api_newsletter_detail", args=[newsletter.pk])

        response = self.client.delete(detail_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )
        self.assertTrue(Newsletter.objects.filter(pk=newsletter.pk).exists())

    def test_journalist_cannot_access_subscribed_articles_endpoint(self):
        self.client.login(username="journalist1", password="TestPass123!")

        response = self.client.get(self.article_subscribed_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )

    @patch("api.views.send_article_approved_email_to_subscribers")
    def test_editor_can_approve_article_and_triggers_subscriber_email(
        self, mock_send_emails
    ):
        # Arrange
        article = Article.objects.create(
            title="Pending article for approval email test",
            content="Content",
            author=self.journalist,
            publisher=self.publisher,
            approved=False,
        )

        self.client.login(
            username=self.editor.username, password="TestPass123!"
        )

        # Act
        response = self.client.post(f"/api/articles/{article.pk}/approve/")

        # Assert
        self.assertEqual(response.status_code, 200)

        article.refresh_from_db()
        self.assertTrue(article.approved)
        self.assertIsNotNone(article.approved_at)
        self.assertEqual(article.approved_by, self.editor)

        mock_send_emails.assert_called_once_with(article)
