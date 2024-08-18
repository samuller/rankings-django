"""Django URL configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/

Examples
--------
- Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
- Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
- Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path, path
from django.contrib import admin
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def openapi_docs(request: HttpRequest) -> HttpResponse:
    """Generate Swagger/OpenAPI docs page."""
    # See: https://www.django-rest-framework.org/topics/documenting-your-api/
    # And: https://github.com/tiangolo/fastapi/blob/master/fastapi/openapi/docs.py
    # And: view-source:https://petstore.swagger.io/
    context = {
        "title": "App - Swagger UI",
        "swagger_favicon_url": "favicon.ico",
        "swagger_css_url": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        "swagger_js_url": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        "openapi_url": "openapi.json",
    }
    return render(request, "swagger.html", context)


urlpatterns = [
    path("api/openapi.json", SpectacularAPIView.as_view(), name="openapi-schema"),
    # Custom generation of Swagger UI docs (used before drf-spectacular)
    path("api/docs", openapi_docs),
    path(
        "api/docs/swagger",
        SpectacularSwaggerView.as_view(url_name="openapi-schema"),
        name="swagger",
    ),
    path(
        "api/docs/redoc",
        SpectacularRedocView.as_view(url_name="openapi-schema"),
        name="redoc",
    ),
    re_path(r"^admin/", include("massadmin.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^", include("previous.urls")),
]
