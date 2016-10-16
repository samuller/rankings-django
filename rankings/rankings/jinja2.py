from __future__ import absolute_import  # Python 2 only

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

from jinja2 import Environment, filters


def no_op(with_categories=False, category_filter=[]):
    return None


def to_json(value):
    return value


def url_for(endpoint, **values):
    if(endpoint == 'static'):
        return staticfiles_storage.url(values.get("filename"))
    return reverse(endpoint, kwargs=values)
    # return endpoint


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'url_for': url_for,
        'get_flashed_messages':  no_op
    })
    env.filters['tojson'] = to_json
    # env.filters['url_for'] = url_for
    # filters.FILTERS['url_for'] = url_for
    return env
