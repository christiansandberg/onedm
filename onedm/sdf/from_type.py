"""Conversion from native types to sdfData."""

from enum import Enum
from typing import Type

from pydantic import TypeAdapter

from .data import Data, IntegerData, StringData
from .json_schema import from_json_schema

DataModel = TypeAdapter(Data)


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

    if "enum" in schema and issubclass(type_, Enum):
        data.choices = {}
        for member in type_:
            if isinstance(member.value, int):
                data.choices[member.name] = IntegerData(const=member.value)
            elif isinstance(member.value, str):
                data.choices[member.name] = StringData(const=member.value)
            else:
                raise TypeError("Unsupported enum type {type_}")
        data.enum = None

    return data
