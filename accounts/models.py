"""
accounts/models.py

Defines the application's custom user model.

This user model extends Django's AbstractUser and adds a role field to support
role-based access control. The user's group membership is kept in sync with
their role when saved.
"""

from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user with a role used for access control.
    """

    email = models.EmailField(unique=True)

    ROLE_READER = "Reader"
    ROLE_EDITOR = "Editor"
    ROLE_JOURNALIST = "Journalist"

    ROLE_CHOICES = (
        (ROLE_READER, "Reader"),
        (ROLE_EDITOR, "Editor"),
        (ROLE_JOURNALIST, "Journalist"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def save(self, *args, **kwargs):
        """
        Save the user and keep their group membership aligned with their role.
        """
        if not self.email:
            self.email = f"{self.username}@example.com"
        super().save(*args, **kwargs)

        role_to_group = {
            self.ROLE_READER: "Reader",
            self.ROLE_EDITOR: "Editor",
            self.ROLE_JOURNALIST: "Journalist",
        }

        target_group_name = role_to_group.get(self.role)
        if not target_group_name:
            return

        # Ensure the role groups exist
        reader_group, _ = Group.objects.get_or_create(name="Reader")
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        journalist_group, _ = Group.objects.get_or_create(name="Journalist")

        # Remove user from all role groups, then add the correct one
        self.groups.remove(reader_group, editor_group, journalist_group)
        self.groups.add(Group.objects.get(name=target_group_name))
