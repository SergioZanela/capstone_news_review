from typing import Any

from rest_framework.permissions import BasePermission, SAFE_METHODS


def _role(user: Any) -> str:
    """Return normalized role string (lowercase) safely."""
    return (getattr(user, "role", "") or "").strip().lower()


class IsEditor(BasePermission):
    """
    Allows access only to editors.
    Supports role field and group fallback.
    """

    message = "Editor role required."

    def has_permission(  # type: ignore[override]
        self, request: Any, view: Any
    ) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # bool(...) keeps type checker happy
        in_editor_group = bool(user.groups.filter(name="Editor").exists())
        return _role(user) == "editor" or in_editor_group


class IsJournalist(BasePermission):
    """
    Allows access only to journalists.
    Supports role field and group fallback.
    """

    message = "Journalist role required."

    def has_permission(  # type: ignore[override]
        self, request: Any, view: Any
    ) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        in_journalist_group = bool(
            user.groups.filter(name="Journalist").exists()
        )
        return _role(user) == "journalist" or in_journalist_group


class CanReadApprovedArticles(BasePermission):
    """
    Object-level rule for article detail:
    - approved articles: any authenticated user can view
    - unapproved articles: editors only
    """

    message = "You do not have permission to view this article."

    def has_object_permission(  # type: ignore[override]
        self, request: Any, view: Any, obj: Any
    ) -> bool:
        if request.method not in SAFE_METHODS:
            return False

        user = request.user
        if not user or not user.is_authenticated:
            return False

        if bool(obj.approved):
            return True

        in_editor_group = bool(user.groups.filter(name="Editor").exists())
        return _role(user) == "editor" or in_editor_group


class IsReader(BasePermission):
    """
    Allows access only to readers.
    Supports role field and group fallback.
    """

    message = "Reader role required."

    def has_permission(  # type: ignore[override]
        self, request: Any, view: Any
    ) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        in_reader_group = bool(user.groups.filter(name="Reader").exists())
        return _role(user) == "reader" or in_reader_group


class IsOwnerOrEditor(BasePermission):
    """
    Object-level permission:
    - owner can access/modify their own object
      (supports reader-owned and author-owned objects)
    - editors are allowed as fallback
    """

    message = "You do not have permission to access this resource."

    def has_object_permission(  # type: ignore[override]
        self, request: Any, view: Any, obj: Any
    ) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        user_id = getattr(user, "id", None)

        # Subscription-style ownership (reader owns object)
        if getattr(obj, "reader_id", None) == user_id:
            return True

        # Article/Newsletter-style ownership (author owns object)
        if getattr(obj, "author_id", None) == user_id:
            return True

        in_editor_group = bool(user.groups.filter(name="Editor").exists())
        return _role(user) == "editor" or in_editor_group


class IsJournalistOrEditor(BasePermission):
    """
    Allows access to journalists or editors.
    Supports role field and group fallback.
    """

    message = "Journalist or Editor role required."

    def has_permission(  # type: ignore[override]
        self, request: Any, view: Any
    ) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = _role(user)
        in_journalist_group = bool(
            user.groups.filter(name="Journalist").exists()
        )
        in_editor_group = bool(user.groups.filter(name="Editor").exists())

        return (
            role in {"journalist", "editor"}
            or in_journalist_group
            or in_editor_group
        )


class IsOwnerOrEditorForNewsletter(BasePermission):
    """
    Object-level permission for Newsletter:
    - owner/author can modify
    - editors can modify any newsletter
    """

    message = "You do not have permission to modify this newsletter."

    def has_object_permission(  # type: ignore[override]
        self, request: Any, view: Any, obj: Any
    ) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(obj, "author_id", None) == getattr(user, "id", None):
            return True

        in_editor_group = bool(user.groups.filter(name="Editor").exists())
        return _role(user) == "editor" or in_editor_group
