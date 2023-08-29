"""Utility functions."""
from typing import Literal, Optional, List, TypedDict

from rest_framework import serializers, authentication
from rest_framework.settings import api_settings
from django.core.exceptions import FieldDoesNotExist
from rest_framework.schemas import openapi


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):
    """
    SessionAuthentication that doesn't require CSRF tokens.

    See: https://stackoverflow.com/questions/30871033/django-rest-framework-remove-csrf
    """

    def enforce_csrf(self, request):
        """Enforce CSRF validation for session based authentication."""
        # Skip CSRF check from happening.
        return


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """Control which fields are serlialzed if an additional `fields` argument is given.

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


class FieldFilterMixin:
    """This mixin allows you to return only a subset of the fields serialized.

    Use with a class extending `rest_framework.viewsets.ModelViewSet` and that is already using a `serializer_class`
    that is based on `DynamicFieldsModelSerializer`.
    """

    # Name of the query parameter to use for filtering fields."""
    field_filter_param: Optional[str] = None

    def get_serializer(self, *args, **kwargs):
        """Return the serializer instance to be used."""
        fields = self.request.query_params.get(self.field_filter_param)
        # Filter fields returned in output.
        if self.field_filter_param is not None and fields is not None:
            if fields == "":
                raise serializers.ValidationError(
                    {"error": f"query parameter '{self.field_filter_param}' is empty"}
                )

            fields = tuple(fields.split(","))
            # Check all the fields are valid.
            all_fields = self.get_serializer_class().Meta.fields
            if not set(fields).issubset(all_fields):
                invalid_fields = list(set(fields) - set(all_fields))
                raise serializers.ValidationError(
                    {
                        "error": f"query parameter '{self.field_filter_param}'"
                        + f" referenced invalid fields: {invalid_fields}"
                    }
                )

            return super().get_serializer(fields=fields, *args, **kwargs)
        return super().get_serializer(*args, **kwargs)


class ValidateParamsMixin:
    """Mixin for validating query parameters.

    Use with a class extending `rest_framework.viewsets.ModelViewSet`.
    """

    extra_allowed_params: List[str] = []

    def get_queryset(self):
        """Get the list of items for this view."""
        # Check first for invalid query parameters.
        allowed_params = [
            api_settings.URL_FORMAT_OVERRIDE,
            *self.extra_allowed_params,
        ]
        if self.field_filter_param:
            allowed_params.append(self.field_filter_param)
        if self.filterset_fields:
            allowed_params.extend(self.filterset_fields)
        if not set(self.request.GET.keys()).issubset(allowed_params):
            invalid_params = list(set(self.request.GET.keys()) - set(allowed_params))
            raise FieldDoesNotExist(f"Invalid parameter: {invalid_params}")

        return super().get_queryset()


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


class ManualAutoSchema(openapi.AutoSchema):
    """An AutoSchema that allows some extra fields to be manually added."""

    def __init__(
        self,
        manual_fields: List[OpenAPIParameters],
        tags=None,
        operation_id_base=None,
        component_name=None,
    ):
        super().__init__(tags, operation_id_base, component_name)
        self.manual_fields = manual_fields

    def get_operation(self, path, method):
        """Get operation schema details of API endpoint."""
        operation = super().get_operation(path, method)
        operation["parameters"].extend(self.manual_fields)
        return operation


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
