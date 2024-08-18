#!/usr/bin/env python3
"""Jinja configurations."""

import json
from typing import Any, List, Dict
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse


from jinja2 import Environment


def no_op(with_categories: bool = False, category_filter: List[str] = []) -> None:
    """Define custom filter to override Flask's `get_flashed_messages`."""
    return None


def to_json(value: Any) -> str:
    """Define custom filter to convert data variable to JSON."""
    if isinstance(value, dict):
        # Clear ModelState left by convert django models to dict's
        value["_state"] = None
    result = json.dumps(value)
    return result


def url_for(endpoint: str, **values: Dict[str, Any]) -> str:
    """Define custom filter to generate URL for Django views or static files."""
    if endpoint == "static":
        return staticfiles_storage.url(values.get("filename"))
    return reverse(endpoint, kwargs=values)


def environment(**options: Dict[str, Any]) -> Environment:
    """Define Jinja environment configurations."""
    env = Environment(**options)
    env.globals.update(
        {
            "static": staticfiles_storage.url,
            "url": reverse,
            "url_for": url_for,
            "get_flashed_messages": no_op,
        }
    )
    env.filters["tojson"] = to_json
    # env.filters['url_for'] = url_for
    # jinja2.filters.FILTERS['url_for'] = url_for
    return env
