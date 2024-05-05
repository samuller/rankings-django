"""Middleware for startup checks of database."""
import os
from pathlib import Path

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed


class CheckDBMiddleware:
    """Check database file and fail hard at start-up if it isn't writable."""

    def __init__(self, get_response):
        db_path = Path(settings.DATABASES["default"]["NAME"])
        if db_path.exists() and not os.access(str(db_path), os.W_OK):
            curr_uid = os.getuid()
            file_uid = os.stat(db_path).st_uid
            cmp_str = f"current vs file UIDs: {curr_uid} vs. {file_uid}"
            raise Exception(f"Database file is not writable: {str(db_path)} ({cmp_str})")
        # Indicate that this middleware won't be used after initialization.
        # See: https://docs.djangoproject.com/en/dev/topics/http/middleware/#marking-middleware-as-unused
        raise MiddlewareNotUsed("Database check completed")
