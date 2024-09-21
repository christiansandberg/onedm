"""Conversion from native types to sdfData."""

from enum import Enum
from typing import Type

from pydantic import TypeAdapter

from .data import Data, IntegerData, StringData
from .json_schema import from_json_schema


def data_from_type(type_: Type) -> Data | None:
    """Create from a native Python or Pydantic type.

    None or null is not a supported type in SDF. In this case the return value
    will be None.
    """
    schema = TypeAdapter(type_).json_schema()

    if schema.get("type") == "null":
        # Null types not supported
        return None

    data = from_json_schema(schema)

    if isinstance(data, IntegerData) and data.enum and issubclass(type_, Enum):
        data.choices = {
            member.name: IntegerData(const=member.value) for member in type_
        }
        data.enum = None

    return data
