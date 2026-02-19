# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import re
from enum import Enum
from typing import Any, Dict, TypeVar
from azure.core import CaseInsensitiveEnumMeta
from azure.core.polling import LROPoller, PollingMethod
from ._models import (
    StringField,
    IntegerField,
    NumberField,
    BooleanField,
    DateField,
    TimeField,
    ArrayField,
    ObjectField,
    JsonField,
    ContentField,
)

# Note: The generated value_* attributes (e.g., value_string, value_number) are renamed
# to just `value` at runtime in patch_sdk() so users access field.value uniformly.

PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

__all__ = [
    "RecordMergePatchUpdate",
    "AnalyzeLROPoller",
    "ProcessingLocation",
    "StringField",
    "IntegerField",
    "NumberField",
    "BooleanField",
    "DateField",
    "TimeField",
    "ArrayField",
    "ObjectField",
    "JsonField",
]

# RecordMergePatchUpdate is a TypeSpec artifact that wasn't generated
# It's just an alias for dict[str, str] for model deployments
RecordMergePatchUpdate = Dict[str, str]


# SDK-FIX: Redefine ProcessingLocation enum with correct member name GLOBAL.
# The typespec-python emitter generates "GLOBALEnum" because "global" is a Python reserved keyword.
# This redefinition restores the expected GLOBAL name and is visible in APIView.
# Must be kept in sync with the generated _enums.ProcessingLocation if new members are added.
class ProcessingLocation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The location where the data may be processed."""

    GEOGRAPHY = "geography"
    """Data may be processed in the same geography as the resource."""
    DATA_ZONE = "dataZone"
    """Data may be processed in the same data zone as the resource."""
    GLOBAL = "global"
    """Data may be processed in any Azure data center globally."""


def _parse_operation_id(operation_location_header: str) -> str:
    """Parse operation ID from Operation-Location header for analyze operations.

    :param operation_location_header: The Operation-Location header value
    :type operation_location_header: str
    :return: The extracted operation ID
    :rtype: str
    :raises ValueError: If operation ID cannot be extracted
    """
    # Pattern: https://endpoint/.../analyzerResults/{operation_id}?api-version=...
    regex = r".*/analyzerResults/([^?/]+)"

    match = re.search(regex, operation_location_header)
    if not match:
        raise ValueError(
            f"Could not extract operation ID from: {operation_location_header}"
        )

    return match.group(1)


class AnalyzeLROPoller(LROPoller[PollingReturnType_co]):
    """Custom LROPoller for Content Understanding analyze operations.

    Provides access to the operation ID for tracking and diagnostics.
    """

    @property
    def operation_id(self) -> str:
        """Returns the operation ID for this long-running operation.

        The operation ID can be used with get_result_file() to retrieve
        intermediate or final result files from the service.

        :return: The operation ID
        :rtype: str
        :raises ValueError: If the operation ID cannot be extracted
        """
        try:
            operation_location = self.polling_method()._initial_response.http_response.headers["Operation-Location"]  # type: ignore # pylint: disable=protected-access
            return _parse_operation_id(operation_location)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Could not extract operation ID: {str(e)}") from e

    @classmethod
    def from_poller(
        cls, poller: LROPoller[PollingReturnType_co]
    ) -> (
        "AnalyzeLROPoller[PollingReturnType_co]"  # pyright: ignore[reportInvalidTypeArguments]
    ):
        """Wrap an existing LROPoller without re-initializing the polling method.

        This avoids duplicate HTTP requests that would occur if we created a new
        LROPoller instance (which calls polling_method.initialize() again).

        :param poller: The existing LROPoller to wrap
        :type poller: ~azure.core.polling.LROPoller
        :return: An AnalyzeLROPoller wrapping the same polling state
        :rtype: AnalyzeLROPoller
        """
        # Create instance without calling __init__ to avoid re-initialization
        instance: "AnalyzeLROPoller[PollingReturnType_co]" = object.__new__(  # pyright: ignore[reportInvalidTypeArguments]
            cls
        )
        # Copy all attributes from the original poller
        instance.__dict__.update(poller.__dict__)
        return instance

    @classmethod
    def from_continuation_token(
        cls,
        polling_method: PollingMethod[PollingReturnType_co],
        continuation_token: str,
        **kwargs: Any,
    ) -> "AnalyzeLROPoller":
        """Create a poller from a continuation token.

        :param polling_method: The polling strategy to adopt
        :type polling_method: ~azure.core.polling.PollingMethod
        :param continuation_token: An opaque continuation token
        :type continuation_token: str
        :return: An instance of AnalyzeLROPoller
        :rtype: AnalyzeLROPoller
        :raises ~azure.core.exceptions.HttpResponseError: If the continuation token is invalid.
        """
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


def _rename_value_field_to_value(field_class: type, old_attr_name: str) -> None:
    """Rename a generated ``value_*`` rest_field to ``value`` on a ContentField subclass.

    The underlying JSON wire name (e.g., ``valueString``) is preserved because the
    ``_RestField`` descriptor stores it in ``_rest_name``.  Only the Python attribute
    name changes so that users access ``field.value`` instead of ``field.value_string``.

    :param field_class: The ContentField subclass to patch (e.g. ``StringField``).
    :type field_class: type
    :param old_attr_name: The generated attribute name to rename (e.g. ``"value_string"``).
    :type old_attr_name: str
    :return: None
    :rtype: None
    """
    descriptor = field_class.__dict__.get(old_attr_name)
    if descriptor is None:
        return

    # Install the same rest_field descriptor under the name ``value``
    setattr(field_class, "value", descriptor)

    # Remove the old attribute name
    try:
        delattr(field_class, old_attr_name)
    except AttributeError:
        pass

    # Migrate annotation so IDE / type-checker support works
    annotations = getattr(field_class, "__annotations__", {})
    if old_attr_name in annotations:
        annotations["value"] = annotations.pop(old_attr_name)

    # Clear the _calculated cache so _attr_to_rest_field is rebuilt on next
    # instantiation with the new attribute name.
    calc_key = f"{field_class.__module__}.{field_class.__qualname__}"
    if hasattr(field_class, "_calculated"):
        field_class._calculated.discard(calc_key)  # type: ignore[union-attr] # pylint: disable=protected-access


def patch_sdk():
    """Patch the SDK to add missing models and convenience properties."""
    from . import _models

    # Add RecordMergePatchUpdate as an alias
    _models.RecordMergePatchUpdate = RecordMergePatchUpdate  # type: ignore[attr-defined]

    # Rename generated value_* rest_field attributes to ``value`` on each
    # ContentField subclass so the public API is simply ``field.value``.
    _rename_value_field_to_value(StringField, "value_string")
    _rename_value_field_to_value(IntegerField, "value_integer")
    _rename_value_field_to_value(NumberField, "value_number")
    _rename_value_field_to_value(BooleanField, "value_boolean")
    _rename_value_field_to_value(DateField, "value_date")
    _rename_value_field_to_value(TimeField, "value_time")
    _rename_value_field_to_value(ArrayField, "value_array")
    _rename_value_field_to_value(ObjectField, "value_object")
    _rename_value_field_to_value(JsonField, "value_json")

    # Add ``value`` annotation on the ContentField base class for type-checker
    # support when code holds a generic ContentField reference.  At runtime the
    # subclass descriptor handles the actual access.
    if not hasattr(ContentField, "__annotations__"):
        ContentField.__annotations__ = {}
    ContentField.__annotations__["value"] = Any

    # SDK-FIX: Patch AudioVisualContent.__init__ to handle KeyFrameTimesMs casing inconsistency
    # The service returns "KeyFrameTimesMs" (capital K) but TypeSpec defines "keyFrameTimesMs" (lowercase k)
    # This fix is forward compatible: if the service fixes the issue and returns "keyFrameTimesMs" correctly,
    # the patch will be a no-op and the correct value will pass through unchanged.
    _original_audio_visual_content_init = _models.AudioVisualContent.__init__  # type: ignore[attr-defined] # pylint: disable=I1101

    def _patched_audio_visual_content_init(self, *args: Any, **kwargs: Any) -> None:
        """Patched __init__ that normalizes casing for KeyFrameTimesMs before calling parent.

        This patch is forward compatible: it only normalizes when the service returns incorrect casing.
        If the service returns the correct "keyFrameTimesMs" casing, the patch does nothing.

        :param args: Positional arguments passed to __init__.
        :type args: Any
        """
        # If first arg is a dict (mapping), normalize the casing
        if args and isinstance(args[0], dict):
            mapping = dict(args[0])  # Make a copy
            # SDK-FIX: Handle both "keyFrameTimesMs" (TypeSpec) and "KeyFrameTimesMs" (service response)
            # Forward compatible: only normalizes if incorrect casing exists and correct casing doesn't
            if "KeyFrameTimesMs" in mapping and "keyFrameTimesMs" not in mapping:
                mapping["keyFrameTimesMs"] = mapping["KeyFrameTimesMs"]
            # Call original with normalized mapping
            args = (mapping,) + args[1:]
        _original_audio_visual_content_init(self, *args, **kwargs)

    _models.AudioVisualContent.__init__ = _patched_audio_visual_content_init  # type: ignore[assignment] # pylint: disable=I1101
