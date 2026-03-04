from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import CustomUser
from news.models import Publisher, PublisherMembership


class UserRoleTests(TestCase):
    def test_user_is_added_to_matching_role_group_on_save(self):
        user = CustomUser.objects.create_user(
            username="reader_user",
            password="TestPass123!",
            role="Reader",
        )

        self.assertTrue(user.groups.filter(name="Reader").exists())
        self.assertFalse(user.groups.filter(name="Editor").exists())
        self.assertFalse(user.groups.filter(name="Journalist").exists())


class PublisherMembershipValidationTests(TestCase):
    def setUp(self):
        self.publisher = Publisher.objects.create(name="City Times")
        self.reader = CustomUser.objects.create_user(
            username="reader1",
            password="TestPass123!",
            role="Reader",
        )
        self.editor = CustomUser.objects.create_user(
            username="editor1",
            password="TestPass123!",
            role="Editor",
        )

    def test_reader_cannot_become_publisher_member(self):
        membership = PublisherMembership(
            publisher=self.publisher,
            user=self.reader,
            member_role="Journalist",
        )

        with self.assertRaises(ValidationError):
            membership.full_clean()

    def test_editor_can_hold_editor_membership(self):
        membership = PublisherMembership(
            publisher=self.publisher,
            user=self.editor,
            member_role="Editor",
        )

        membership.full_clean()
