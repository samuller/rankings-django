"""Utility functions."""
from typing import Optional
from rest_framework import serializers, authentication, viewsets


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


class ModelSubViewSet(viewsets.ModelViewSet):
    """A ModelViewSet that also allows you to view only a subset of the serialized fields.

    Requires that you're already using a `serializer_class` that is based on `DynamicFieldsModelSerializer`.
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
