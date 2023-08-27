"""Utility functions."""
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication that doesn't require CSRF tokens.

    See: https://stackoverflow.com/questions/30871033/django-rest-framework-remove-csrf
    """

    def enforce_csrf(self, request):
        """Enforce CSRF validation for session based authentication."""
        # Skip CSRF check from happening.
        return


def cardinalToOrdinal(num: int) -> str:
    """Convert a cardinal number (how many) to an ordinal number string (which position)."""
    suffix = {
        1: "st",
        2: "nd",
        3: "rd",
    }.get(num % 10, "th")
    suffix = {
        11: "th",
        12: "th",
        13: "th",
    }.get(num % 100, suffix)

    return str(num) + suffix
