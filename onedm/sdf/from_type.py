"""Conversion from native types to sdfData."""

from typing import Type

from pydantic import TypeAdapter
from pydantic.json_schema import GenerateJsonSchema
from pydantic_core import core_schema

from . import data

DataAdapter: TypeAdapter[data.Data] = TypeAdapter(data.Data)


def data_from_type(type_: Type) -> data.Data | None:
    """Create from a native Python or Pydantic type.

    None or null is not a supported type in SDF. In this case the return value
    will be None.
    """
    definition = definition_from_type(type_)
    if definition.get("type") == "null":
        # Not supported in SDF
        return None
    return DataAdapter.validate_python(definition)


def definition_from_type(type_: Type) -> dict:
    return TypeAdapter(type_).json_schema(
        ref_template="#/sdfData/{model}", schema_generator=GenerateSDF
    )


class GenerateSDF(GenerateJsonSchema):
    """Handles the differences between JSON schema and SDF

    Note that the Pydantic SDF models converts '$ref' and 'title' to 'sdfRef'
    and 'label'.
    """

    def generate_inner(self, schema: core_schema.CoreSchema):
        definition = super().generate_inner(schema)
        # In SDF everything is nullable by default while in JSON schema it is not
        definition.setdefault("nullable", False)
        return definition

    def nullable_schema(self, schema: core_schema.NullableSchema):
        definition = self.generate_inner(schema["schema"])
        # SDF uses the nullable attribute rather than anyOf/oneOf
        definition["nullable"] = True
        return definition

    def enum_schema(self, schema: core_schema.EnumSchema):
        definition = super().enum_schema(schema)
        if "enum" in definition:
            # Replace enum with sdfChoice
            definition["sdfChoice"] = {
                member.name: {"const": member.value} for member in schema["members"]
            }
            del definition["enum"]
        return definition

    def union_schema(self, schema: core_schema.UnionSchema):
        definition = super().union_schema(schema)
        definition["sdfChoice"] = {
            f"choice-{i}": choice
            for i, choice in enumerate(definition["anyOf"], start=1)
        }
        del definition["anyOf"]
        return definition

    def bytes_schema(self, schema: core_schema.BytesSchema):
        definition = super().bytes_schema(schema)
        definition["sdfType"] = "byte-string"
        return definition

    def timedelta_schema(self, schema: core_schema.TimedeltaSchema):
        definition = super().timedelta_schema(schema)
        if definition["type"] == "number":
            definition["unit"] = "s"
        return definition
