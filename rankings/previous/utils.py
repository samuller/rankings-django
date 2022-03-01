"""Utility functions."""


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
