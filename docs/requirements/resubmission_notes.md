# Resubmission Notes

## Missing modules fix

The original submission listed `core` and `integrations` in `INSTALLED_APPS`, but those directories were only empty placeholders and were not used by any implemented feature.

For the resubmission:
- the unused app references were removed from `config/settings.py`
- the existing implemented apps remain: `accounts`, `news`, and `api`

## MariaDB fix

The original submission used SQLite. The project is now configured for MariaDB through Django's MySQL backend using the `PyMySQL` driver.

Environment variables expected by the project:
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

## User roles/use cases still present

The implemented roles and their use cases remain in the active apps:
- **Reader**: read approved content, subscribe/unsubscribe to publishers and journalists
- **Journalist**: create articles and newsletters
- **Editor**: approve/reject articles, manage editorial actions

The role and permission logic remains in:
- `accounts/models.py`
- `accounts/signals.py`
- `api/permissions.py`
- `news/views.py` and `api/views.py`
