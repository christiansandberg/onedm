"""Conversion from native types to sdfData."""

from typing import Any, NamedTuple, Type

from pydantic import TypeAdapter
from pydantic.json_schema import GenerateJsonSchema
from pydantic_core import core_schema

from . import data

data_adapter: TypeAdapter[data.Data] = TypeAdapter(data.Data)


class ModelResult(NamedTuple):
    definition: dict[str, Any]
    map: dict[str, dict]


def data_from_type(type_: Type) -> data.Data:
    """Create from a native Python or Pydantic type

    This function will create a resolved data model, which means it will not
    work with recursive models. Use unresolved_data_from_type for that purpose.
    """
    schema = TypeAdapter(type_).json_schema(
        schema_generator=GenerateResolvedSDF, mode="serialization"
    )
    return data_adapter.validate_python(schema)


def unresolved_data_from_type(
    type_: Type, ref_template="#/sdfData/{model}"
) -> ModelResult:
    """Create an unresolved definition

    The result is a tuple of the raw definition as a dict and a mapping from
    ref pointer names to their definitions.
    The data definitions must be placed according to the pointers in the final
    document.

    Example:

        class MyEnum(enum.IntEnum):
            ONE = 1

        definition, data = unresolved_data_from_type(MyEnum)
        # {"sdfRef": "#/sdfData/MyEnum"}
        #
        # {
        #     "#/sdfData/MyEnum": {...}
        # }

    These can then be used to merge multiple definitions into a document or
    when using recursive models.
    """
    schema = TypeAdapter(type_).json_schema(
        ref_template=ref_template, schema_generator=GenerateSDF, mode="serialization"
    )
    defs: dict[str, dict] = schema.pop("$defs", {})
    data_map = {ref_template.format(model=name): model for name, model in defs.items()}
    return ModelResult(schema, data_map)


class GenerateSDF(GenerateJsonSchema):
    """Handles the differences between JSON schema and SDF"""

    def generate_inner(self, schema: core_schema.CoreSchema):
        definition = super().generate_inner(schema)

        # SDF use sdfRef instead of $ref
        if "$ref" in definition:
            definition["sdfRef"] = definition["$ref"]
            # Pydantic needs the $ref key, so leave it for now
            # del definition["$ref"]

        # SDF use label instead of title
        if "title" in definition:
            definition["label"] = definition.pop("title")

        # In SDF everything is nullable by default while in JSON schema it is not
        definition.setdefault("nullable", False)

        return definition

    def nullable_schema(self, schema: core_schema.NullableSchema):
        definition = self.generate_inner(schema["schema"])
        # SDF uses the nullable attribute rather than anyOf/oneOf
        definition["nullable"] = True
        return definition

    def none_schema(self, schema: core_schema.NoneSchema):
        # Null types are not supported, replace with "const": null
        return {"const": None}

    def literal_schema(self, schema: core_schema.LiteralSchema):
        definition = super().literal_schema(schema)
        # Null types are not supported, replace with "const": null
        if definition.get("type") == "null":
            del definition["type"]
            definition["const"] = None
        return definition

    def tuple_schema(self, schema: core_schema.TupleSchema):
        definition = super().tuple_schema(schema)
        # SDF does not support tuples, allow any item type
        if "prefixItems" in definition:
            del definition["prefixItems"]
        definition["items"] = {}
        return definition

    def enum_schema(self, schema: core_schema.EnumSchema):
        definition = super().enum_schema(schema)
        definition["sdfChoice"] = {
            member.name: {"const": member.value} for member in schema["members"]
        }
        if "enum" in definition:
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


class GenerateResolvedSDF(GenerateSDF):
    """Generate a resolved SDF model"""

    def generate_inner(self, schema: core_schema.CoreSchema):
        if "ref" in schema:
            del schema["ref"]  # type: ignore
        return super().generate_inner(schema)
