"""Conversion from native types to sdfData."""

from typing import Type

from pydantic import TypeAdapter
from pydantic.json_schema import GenerateJsonSchema
from pydantic_core import core_schema

from . import data

DataAdapter: TypeAdapter[data.Data] = TypeAdapter(data.Data)


def data_from_type(type_: Type) -> data.Data:
    """Create from a native Python or Pydantic type"""
    definition = definition_from_type(type_)
    return DataAdapter.validate_python(definition)


def definition_from_type(type_: Type) -> dict:
    return TypeAdapter(type_).json_schema(
        ref_template="#/sdfData/{model}", schema_generator=GenerateSDF
    )


class GenerateSDF(GenerateJsonSchema):
    """Handles the differences between JSON schema and SDF"""

    def generate_inner(self, schema: core_schema.CoreSchema):
        if "ref" in schema:
            # Only generate dereferenced schemas for now
            del schema["ref"]  # type: ignore
        definition = super().generate_inner(schema)
        # In SDF everything is nullable by default while in JSON schema it is not
        definition.setdefault("nullable", False)
        return definition

    def nullable_schema(self, schema: core_schema.NullableSchema):
        definition = self.generate_inner(schema["schema"])
        # SDF uses the nullable attribute rather than anyOf/oneOf
        definition["nullable"] = True
        return definition

    def none_schema(self, schema: core_schema.NoneSchema):
        return {"const": None}

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
        choices = {}
        for choice in schema["choices"]:
            if isinstance(choice, tuple):
                choice_schema, name = choice
                choices[name] = self.generate_inner(choice_schema)
            elif "type" in choice:
                choices[choice["type"]] = self.generate_inner(choice)
        return {"sdfChoice": choices}

    def bytes_schema(self, schema: core_schema.BytesSchema):
        definition = super().bytes_schema(schema)
        definition["sdfType"] = "byte-string"
        return definition

    def timedelta_schema(self, schema: core_schema.TimedeltaSchema):
        definition = super().timedelta_schema(schema)
        if definition["type"] == "number":
            definition["unit"] = "s"
        return definition
