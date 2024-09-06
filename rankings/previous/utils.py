"""Utility functions."""

from typing import TYPE_CHECKING, Any, List, Literal, Optional, Protocol, Type, TypedDict

from rest_framework import authentication, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):
    """
    SessionAuthentication that doesn't require CSRF tokens.

    See: https://stackoverflow.com/questions/30871033/django-rest-framework-remove-csrf
    """

    def enforce_csrf(self, request):
        """Enforce CSRF validation for session based authentication."""
        # Skip CSRF check from happening.
        return


class FieldFilterModelSerializer(serializers.ModelSerializer):
    """Control which fields are serlialized if an additional `fields` argument is given.

    Source: https://www.django-rest-framework.org/api-guide/serializers/#examples
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


if TYPE_CHECKING:  # pragma: no cover

    class ModelViewSetProtocol(Protocol):
        """Protocol for rest_framework.viewsets.ModelViewSet."""

        # Property from django.views.generic.base.View
        @property
        def request(self): ...  # noqa: D102

        # Property from rest_framework.filters.SearchFilter
        @property
        def search_fields(self): ...  # noqa: D102

        # Property from django.filters.FilterSet
        @property
        def filterset_fields(self): ...  # noqa: D102

        # Properties and methods from rest_framework.generics.GenericAPIView
        @property
        def paginator(self): ...  # noqa: D102

        def get_serializer_class(self: Any) -> Type[Any]: ...  # noqa: D102

    class FieldFilterMixinProtocol(Protocol):
        """Protocol for FieldFilterMixin."""

        @property
        def field_filter_param(self): ...  # noqa: D102
else:

    class ModelViewSetProtocol: ...  # noqa: D101

    class FieldFilterMixinProtocol: ...  # noqa: D101


class FieldFilterMixin(ModelViewSetProtocol):
    """Mixin that allows you to return only a subset of the fields serialized.

    Use with a class extending `rest_framework.viewsets.ModelViewSet` and that is already using a `serializer_class`
    that is based on `DynamicFieldsModelSerializer`.
    """

    # Name of the query parameter to use for filtering fields."""
    field_filter_param: Optional[str] = None

    def get_serializer(self, *args: Any, **kwargs: Any) -> serializers.Serializer:
        """Return the serializer instance to be used."""
        fields = self.request.query_params.get(self.field_filter_param)
        # Filter fields returned in output.
        if self.field_filter_param is not None and fields is not None:
            if fields == "":
                raise ValidationError(f"query parameter '{self.field_filter_param}' is empty")

            fields = tuple(fields.split(","))
            # Check all the fields are valid.
            all_fields = self.get_serializer_class().Meta.fields
            if not set(fields).issubset(all_fields):
                invalid_fields = list(set(fields) - set(all_fields))
                raise ValidationError(
                    f"query parameter '{self.field_filter_param}' referenced invalid fields: {invalid_fields}"
                )

            return super().get_serializer(*args, fields=fields, **kwargs)  # type: ignore
        return super().get_serializer(*args, **kwargs)  # type: ignore


class ValidateParamsMixin(ModelViewSetProtocol, FieldFilterMixinProtocol):
    """Mixin for validating query parameters.

    Use with a class extending `rest_framework.viewsets.ModelViewSet`.
    """

    extra_allowed_params: List[str] = []

    def get_queryset(self):
        """Get the list of items for this view."""
        # Build up a list of all the expected/allowed query parameters.
        allowed_params = [
            api_settings.ORDERING_PARAM,
            api_settings.VERSION_PARAM,
            # Pagination params.
            *[param["name"] for param in self.paginator.get_schema_operation_parameters(None)],
            *self.extra_allowed_params,
        ]
        if api_settings.URL_FORMAT_OVERRIDE is not None:
            allowed_params.append(api_settings.URL_FORMAT_OVERRIDE)
        if self.search_fields is not None:
            allowed_params.append(api_settings.SEARCH_PARAM)
        if self.field_filter_param is not None:
            allowed_params.append(self.field_filter_param)
        if self.filterset_fields:
            allowed_params.extend(self.filterset_fields)
        # Check for any invalid query parameters.
        if not set(self.request.GET.keys()).issubset(allowed_params):
            invalid_params = list(set(self.request.GET.keys()) - set(allowed_params))
            raise ValidationError(f"Invalid parameter: {invalid_params}")

        return super().get_queryset()  # type: ignore


# Need to use TypedDict's function syntax due to reserved keywords in Python ("in", "type").
# See: https://stackoverflow.com/questions/73001554/how-to-define-a-typeddict-class-with-keys-containing-hyphens
OpenAPIParameterSchema = TypedDict("OpenAPIParameterSchema", {"type": str})
OpenAPIParameters = TypedDict(
    "OpenAPIParameters",
    {
        "name": str,
        "in": Literal["query", "path"],
        "required": bool,
        "description": str,
        "schema": OpenAPIParameterSchema,
    },
    total=False,
)


def cardinal_to_ordinal(num: int) -> str:
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
