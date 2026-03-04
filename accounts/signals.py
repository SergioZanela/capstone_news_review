"""
accounts/signals.py

Signals for:
- Creating default role groups and permissions after migrations
- Automatically assigning a user to the correct group based on their role
"""

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import CustomUser


@receiver(post_migrate)
def ensure_role_groups(sender, **kwargs):
    """
    Creates role groups and assigns permissions.
    This is safe to run multiple times.
    """
    if sender.name != "accounts":
        return

    reader_group, _ = Group.objects.get_or_create(name="Reader")
    editor_group, _ = Group.objects.get_or_create(name="Editor")
    journalist_group, _ = Group.objects.get_or_create(name="Journalist")

    Article = apps.get_model("news", "Article")
    Newsletter = apps.get_model("news", "Newsletter")
    Publisher = apps.get_model("news", "Publisher")

    def perms(model, codenames):
        return Permission.objects.filter(
            content_type__app_label=model._meta.app_label,
            content_type__model=model._meta.model_name,
            codename__in=codenames,
        )

    # Default Django model perms: add/change/delete/view
    reader_group.permissions.set(
        list(perms(Article, ["view_article"]))
        + list(perms(Newsletter, ["view_newsletter"]))
        + list(perms(Publisher, ["view_publisher"]))
    )

    editor_group.permissions.set(
        list(perms(Article, [
            "view_article", "change_article", "delete_article"
        ]))
        + list(perms(Newsletter, [
            "view_newsletter", "change_newsletter", "delete_newsletter"
        ]))
        + list(perms(Publisher, ["view_publisher"]))
    )

    journalist_group.permissions.set(
        list(perms(Article, [
            "add_article", "view_article", "change_article", "delete_article"
        ]))
        + list(perms(Newsletter, [
            "add_newsletter", "view_newsletter", "change_newsletter",
            "delete_newsletter"
        ]))
        + list(perms(Publisher, ["view_publisher"]))
    )


@receiver(post_save, sender=CustomUser)
def assign_group_from_role(sender, instance, **kwargs):
    """
    Keeps the user's group in sync with their role.
    """
    role_to_group = {
        CustomUser.ROLE_READER: "Reader",
        CustomUser.ROLE_EDITOR: "Editor",
        CustomUser.ROLE_JOURNALIST: "Journalist",
    }

    target_group_name = role_to_group.get(instance.role)
    if not target_group_name:
        return

    # Ensure the 3 groups exist
    reader_group, _ = Group.objects.get_or_create(name="Reader")
    editor_group, _ = Group.objects.get_or_create(name="Editor")
    journalist_group, _ = Group.objects.get_or_create(name="Journalist")

    # Remove from all 3, then add correct one
    instance.groups.remove(reader_group, editor_group, journalist_group)
    instance.groups.add(Group.objects.get(name=target_group_name))
