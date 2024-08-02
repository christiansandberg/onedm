"""Conversion from native types to sdfData."""

from enum import Enum
from typing import Type

from pydantic import TypeAdapter

from .data import Data

DataModel = TypeAdapter(Data)


def data_from_type(type_: Type) -> Data | None:
    """Create from a native Python or Pydantic type."""
    definition = TypeAdapter(type_).json_schema()

    definition = dereference(definition, definition)

    if "anyOf" in definition:
        definition = flatten_anyof(definition["anyOf"])
    else:
        # Can't be null
        definition["nullable"] = False

    if "title" in definition:
        # SDF uses label instead of title
        definition["label"] = definition.pop("title")

    if "enum" in definition:
        # Could maybe be replaced with sdfChoice
        definition = convert_enum(definition, type_)

    if definition.get("type") == "null":
        return None

    return DataModel.validate_python(definition)


def dereference(definition: dict, root: dict) -> dict:
    if "$ref" in definition:
        ref: str = definition.pop("$ref")
        # Try to dereference for now, in the future we may want to use
        # sdfData to store definitions
        fragments: list[str] = ref.split("/")
        assert fragments[0] == "#", "Only internal references supported"
        definition = root
        for fragment in fragments[1:]:
            definition = definition[fragment]

    if "items" in definition:
        definition["items"] = dereference(definition["items"], root)

    if "properties" in definition:
        for key, value in definition["properties"].items():
            definition["properties"][key] = dereference(value, root)

    return definition


def flatten_anyof(anyof: list[dict]) -> dict:
    nullable = False
    for option in anyof:
        if option["type"] == "null":
            # Replace this null option with nullable property
            nullable = True
            anyof.remove(option)
    if len(anyof) > 1:
        # TODO: Use sdfChoice
        raise NotImplementedError("Unions not supported yet")
    # Flatten
    definition = anyof[0]
    definition["nullable"] = nullable
    return definition


def convert_enum(definition: dict, type_: Type) -> dict:
    if len(definition["enum"]) == 1:
        # Probably means its a constant
        definition["const"] = definition["enum"][0]
        del definition["enum"]
    elif issubclass(type_, Enum):
        definition["sdfChoice"] = {
            member.name: {"const": member.value, "nullable": False} for member in type_
        }
        del definition["enum"]
    return definition
