"""Conversion from native types to sdfData."""

from typing import Type

from pydantic import TypeAdapter
from pydantic_core import core_schema

from . import data


def data_from_type(type_: Type) -> data.Data | None:
    """Create from a native Python or Pydantic type.

    None or null is not a supported type in SDF. In this case the return value
    will be None.
    """
    schema = TypeAdapter(type_).core_schema
    if schema["type"] == "none":
        return None
    return data_from_schema(schema)


def data_from_schema(schema: core_schema.CoreSchema) -> data.Data:
    schema_type = schema["type"]
    data_type: data.Data
    if schema_type == "nullable":
        data_type = data_from_nullable_schema(schema)  # type: ignore
    elif schema_type == "default":
        data_type = data_from_default_schema(schema)  # type: ignore
    elif schema_type == "any":
        data_type = data_from_any_schema(schema)  # type: ignore
    elif schema_type == "int":
        data_type = data_from_int_schema(schema)  # type: ignore
    elif schema_type == "float":
        data_type = data_from_float_schema(schema)  # type: ignore
    elif schema_type == "bool":
        data_type = data_from_bool_schema(schema)  # type: ignore
    elif schema_type == "str":
        data_type = data_from_str_schema(schema)  # type: ignore
    elif schema_type == "bytes":
        data_type = data_from_bytes_schema(schema)  # type: ignore
    elif schema_type == "model":
        data_type = data_from_model_schema(schema)  # type: ignore
    elif schema_type == "model-fields":
        data_type = data_from_model_fields_schema(schema)  # type: ignore
    elif schema_type == "dataclass":
        data_type = data_from_dataclass_schema(schema)  # type: ignore
    elif schema_type == "list":
        data_type = data_from_list_schema(schema)  # type: ignore
    elif schema_type == "set":
        data_type = data_from_set_schema(schema)  # type: ignore
    elif schema_type == "dict":
        data_type = data_from_dict_schema(schema)  # type: ignore
    elif schema_type == "typed-dict":
        data_type = data_from_typed_dict_schema(schema)  # type: ignore
    elif schema_type == "enum":
        data_type = data_from_enum_schema(schema)  # type: ignore
    elif schema_type == "literal":
        data_type = data_from_literal_schema(schema)  # type: ignore
    elif schema_type == "datetime":
        data_type = data_from_datetime_schema(schema)  # type: ignore
    else:
        raise NotImplementedError(f"Unsupported schema '{schema['type']}'")

    # data_type.label = schema["metadata"].get("title")
    return data_type


def data_from_any_schema(schema: core_schema.AnySchema):
    return data.AnyData(nullable=False)


def data_from_nullable_schema(schema: core_schema.NullableSchema):
    data_type = data_from_schema(schema["schema"])
    data_type.nullable = True
    return data_type


def data_from_default_schema(schema: core_schema.WithDefaultSchema):
    data_type = data_from_schema(schema["schema"])
    data_type.default = schema["default"]
    return data_type


def data_from_model_schema(schema: core_schema.ModelSchema):
    return data_from_schema(schema["schema"])


def data_from_model_fields_schema(schema: core_schema.ModelFieldsSchema):
    return data.ObjectData(
        label=schema.get("model_name"),
        properties={
            field.get("serialization_alias", name): data_from_schema(field["schema"])
            for name, field in schema["fields"].items()
        },
        required=[
            field.get("serialization_alias", name)
            for name, field in schema["fields"].items()
            if field["schema"]["type"] != "default"
        ],
        nullable=False,
    )


def data_from_dataclass_args_schema(schema: core_schema.DataclassArgsSchema):
    return data.ObjectData(
        properties={
            field.get("serialization_alias", field["name"]): data_from_schema(
                field["schema"]
            )
            for field in schema["fields"]
        },
        nullable=False,
    )


def data_from_dataclass_schema(schema: core_schema.DataclassSchema):
    return data_from_dataclass_args_schema(schema["schema"])  # type: ignore


def data_from_typed_dict_schema(schema: core_schema.TypedDictSchema):
    return data.ObjectData(
        properties={
            field.get("serialization_alias", name): data_from_schema(field["schema"])
            for name, field in schema["fields"].items()
        },
        required=[
            field.get("serialization_alias", name)
            for name, field in schema["fields"].items()
            if field.get("required", False)
        ],
        nullable=False,
    )


def data_from_list_schema(schema: core_schema.ListSchema):
    return data.ArrayData(
        items=(
            data_from_schema(schema["items_schema"])
            if "items_schema" in schema
            else None
        ),
        min_items=schema.get("min_length", 0),
        max_items=schema.get("max_length"),
        nullable=False,
    )


def data_from_set_schema(schema: core_schema.SetSchema):
    return data.ArrayData(
        items=(
            data_from_schema(schema["items_schema"])
            if "items_schema" in schema
            else None
        ),
        min_items=schema.get("min_length", 0),
        max_items=schema.get("max_length"),
        unique_items=True,
        nullable=False,
    )


def data_from_dict_schema(schema: core_schema.DictSchema):
    return data.ObjectData(nullable=False)


def data_from_int_schema(schema: core_schema.IntSchema):
    return data.IntegerData(
        minimum=schema.get("ge"),
        maximum=schema.get("le"),
        exclusive_minimum=schema.get("gt"),
        exclusive_maximum=schema.get("lt"),
        multiple_of=schema.get("multiple_of"),
        nullable=False,
    )


def data_from_float_schema(schema: core_schema.FloatSchema):
    return data.NumberData(
        minimum=schema.get("ge"),
        maximum=schema.get("le"),
        exclusive_minimum=schema.get("gt"),
        exclusive_maximum=schema.get("lt"),
        multiple_of=schema.get("multiple_of"),
        nullable=False,
    )


def data_from_bool_schema(schema: core_schema.BoolSchema):
    return data.BooleanData(nullable=False)


def data_from_str_schema(schema: core_schema.StringSchema):
    return data.StringData(
        pattern=schema.get("pattern"),
        min_length=schema.get("min_length", 0),
        max_length=schema.get("max_length"),
        nullable=False,
    )


def data_from_bytes_schema(schema: core_schema.BytesSchema):
    return data.StringData(
        sdf_type="byte-string",
        format="bytes",
        min_length=schema.get("min_length", 0),
        max_length=schema.get("max_length"),
        nullable=False,
    )


def data_from_literal_schema(schema: core_schema.LiteralSchema):
    choices = schema["expected"]
    if len(choices) == 1:
        return data.AnyData(const=choices[0], nullable=False)
    if all(isinstance(choice, str) for choice in choices):
        return data.StringData(enum=choices, nullable=False)
    raise NotImplementedError(f"Literal with {choices} not supported")


def data_from_enum_schema(schema: core_schema.EnumSchema):
    if "sub_type" not in schema:
        return data.AnyData(
            choices={
                member.name: data.AnyData(const=member.value)
                for member in schema["members"]
            },
            nullable=False,
        )
    if schema["sub_type"] == "int":
        return data.IntegerData(
            choices={
                member.name: data.IntegerData(const=member.value)
                for member in schema["members"]
            },
            nullable=False,
        )
    if schema["sub_type"] == "str":
        return data.StringData(
            choices={
                member.name: data.StringData(const=member.value)
                for member in schema["members"]
            },
            nullable=False,
        )


def data_from_datetime_schema(schema: core_schema.DatetimeSchema):
    return data.StringData(nullable=False, format="date-time")
