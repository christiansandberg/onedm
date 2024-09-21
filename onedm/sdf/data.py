"""Data qualities.

Contains data qualities as defined by the standard, but divided into separate
types for correct validation and type hints.
"""

from __future__ import annotations

from abc import ABC
import datetime
import enum
from typing import Annotated, Any, Literal, Type, Union

from pydantic import Field, NonNegativeInt, field_serializer
from pydantic_core import SchemaValidator, core_schema

from .common import CommonQualities


class DataQualities(CommonQualities, ABC):
    """Base class for all data qualities."""

    type: Literal["boolean", "number", "integer", "string", "object", "array", None]
    sdf_type: Annotated[str, Field(pattern=r"^[a-z][\-a-z0-9]*$")] | None = None
    nullable: bool = True
    const: Any | None = None
    default: Any | None = None
    choices: Annotated[dict[str, Data] | None, Field(alias="sdfChoice")] = None

    def _get_base_schema(self) -> core_schema.CoreSchema:
        """Implemented by sub-classes."""
        raise NotImplementedError

    def get_pydantic_schema(self) -> core_schema.CoreSchema:
        """Get the Pydantic schema for this data quality."""
        schema: core_schema.CoreSchema

        if self.const is not None:
            schema = core_schema.literal_schema([self.const])
        elif self.choices is not None:
            schema = core_schema.union_schema(
                [
                    (choice.get_pydantic_schema(), name)
                    for name, choice in self.choices.items()
                ]
            )
        else:
            schema = self._get_base_schema()

        if self.default is not None:
            schema = core_schema.with_default_schema(schema, default=self.default)
        if self.nullable:
            schema = core_schema.nullable_schema(schema)
        return schema

    def validate_input(self, input: Any) -> Any:
        """Validate and coerce a value."""
        return SchemaValidator(self.get_pydantic_schema()).validate_python(input)


class NumberData(DataQualities):
    type: Literal["number"] = "number"
    unit: str | None = None
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None
    multiple_of: float | None = None
    format: str | None = None
    const: float | None = None
    default: float | None = None

    @field_serializer("type")
    def always_include_type(self, type: str, _):
        return type

    def _get_base_schema(self) -> core_schema.CoreSchema:
        if self.sdf_type == "unix-time":
            return core_schema.datetime_schema(
                ge=(
                    datetime.datetime.fromtimestamp(self.minimum)
                    if self.minimum is not None
                    else None
                ),
                le=(
                    datetime.datetime.fromtimestamp(self.maximum)
                    if self.maximum is not None
                    else None
                ),
                gt=(
                    datetime.datetime.fromtimestamp(self.exclusive_minimum)
                    if self.exclusive_minimum is not None
                    else None
                ),
                lt=(
                    datetime.datetime.fromtimestamp(self.exclusive_maximum)
                    if self.exclusive_maximum is not None
                    else None
                ),
            )
        return core_schema.float_schema(
            ge=self.minimum,
            le=self.maximum,
            gt=self.exclusive_minimum,
            lt=self.exclusive_maximum,
            multiple_of=self.multiple_of,
        )


class IntegerData(DataQualities):
    type: Literal["integer"] = "integer"
    unit: str | None = None
    minimum: int | None = None
    maximum: int | None = None
    exclusive_minimum: int | None = None
    exclusive_maximum: int | None = None
    multiple_of: int | None = None
    enum: list[int] | None = None
    choices: Annotated[dict[str, IntegerData] | None, Field(alias="sdfChoice")] = None  # type: ignore[assignment]
    const: int | None = None
    default: int | None = None

    @field_serializer("type")
    def always_include_type(self, type: str, _):
        return type

    def _get_base_schema(self) -> core_schema.IntSchema:
        return core_schema.int_schema(
            ge=self.minimum,
            le=self.maximum,
            gt=self.exclusive_minimum,
            lt=self.exclusive_maximum,
            multiple_of=self.multiple_of,
        )

    def to_enum(self) -> enum.EnumMeta | None:
        if self.choices is None:
            return None
        return enum.IntEnum(
            self.label or "Enum",
            {
                name: choice.const
                for name, choice in self.choices.items()
                if choice.const is not None
            },
        )

    def validate_input(self, input: Any) -> enum.IntEnum | int:
        value = SchemaValidator(self.get_pydantic_schema()).validate_python(input)
        # Convert to enum.IntEnum if possible
        if self.choices is not None:
            try:
                value = self.to_enum()(value)
            except ValueError:
                pass
        return value


class BooleanData(DataQualities):
    type: Literal["boolean"] = "boolean"
    const: bool | None = None
    default: bool | None = None
    choices: Annotated[dict[str, BooleanData] | None, Field(alias="sdfChoice")] = None  # type: ignore[assignment]

    @field_serializer("type")
    def always_include_type(self, type: str, _):
        return type

    def _get_base_schema(self) -> core_schema.BoolSchema:
        return core_schema.bool_schema()


class StringData(DataQualities):
    type: Literal["string"] = "string"
    enum: list[str] | None = None
    min_length: NonNegativeInt = 0
    max_length: NonNegativeInt | None = None
    pattern: str | None = None
    format: str | None = None
    content_format: str | None = None
    choices: Annotated[dict[str, StringData] | None, Field(alias="sdfChoice")] = None  # type: ignore[assignment]
    const: str | None = None
    default: str | None = None

    @field_serializer("type")
    def always_include_type(self, type: str, _):
        return type

    def _get_base_schema(self) -> core_schema.CoreSchema:
        if self.enum is not None:
            return core_schema.literal_schema(self.enum)
        if self.sdf_type == "byte-string" or self.format == "bytes":
            return core_schema.bytes_schema(
                min_length=self.min_length, max_length=self.max_length
            )
        if self.format == "uuid":
            return core_schema.uuid_schema()
        if self.format == "date-time":
            return core_schema.datetime_schema()
        if self.format == "date":
            return core_schema.date_schema()
        if self.format == "time":
            return core_schema.time_schema()
        if self.format == "uri":
            return core_schema.url_schema()
        return core_schema.str_schema(
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
        )


class ArrayData(DataQualities):
    type: Literal["array"] = "array"
    items: Data
    min_items: NonNegativeInt = 0
    max_items: NonNegativeInt | None = None
    unique_items: bool = False
    const: list | None = None
    default: list | None = None

    @field_serializer("type")
    def always_include_type(self, type: str, _):
        return type

    def _get_base_schema(self) -> core_schema.ListSchema | core_schema.SetSchema:
        if self.unique_items:
            return core_schema.set_schema(
                self.items.get_pydantic_schema(),
                min_length=self.min_items,
                max_length=self.max_items,
            )
        return core_schema.list_schema(
            self.items.get_pydantic_schema(),
            min_length=self.min_items,
            max_length=self.max_items,
        )


class ObjectData(DataQualities):
    type: Literal["object"] = "object"
    properties: dict[str, Data]
    required: list[str] = Field(default_factory=list)
    const: dict[str, Any] | None = None
    default: dict[str, Any] | None = None

    @field_serializer("type")
    def always_include_type(self, type: str, _):
        return type

    def _get_base_schema(self) -> core_schema.TypedDictSchema:
        required = self.required or []
        fields = {
            name: core_schema.typed_dict_field(
                property.get_pydantic_schema(), required=name in required
            )
            for name, property in self.properties.items()
        }
        return core_schema.typed_dict_schema(fields)


class AnyData(DataQualities):
    type: Literal[None] = None

    def _get_base_schema(self) -> core_schema.AnySchema:
        return core_schema.any_schema()


Data = Union[
    Annotated[
        IntegerData | NumberData | BooleanData | StringData | ObjectData | ArrayData,
        Field(discriminator="type"),
    ],
    AnyData,
]

ObjectData.model_rebuild()
ArrayData.model_rebuild()
