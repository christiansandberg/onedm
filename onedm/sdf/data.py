"""Data qualities.

Contains data qualities as defined by the standard, but divided into separate
types for correct validation and type hints.
"""

from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import Annotated, Any, Literal, Union

from pydantic import Field, NonNegativeInt, model_validator
from pydantic_core import SchemaValidator, core_schema

from .common import CommonQualities


class DataType(str, Enum):
    BOOLEAN = "boolean"
    NUMBER = "number"
    INTEGER = "integer"
    STRING = "string"
    OBJECT = "object"
    ARRAY = "array"


class DataQualities(CommonQualities, ABC):
    """Base class for all data qualities."""

    type: DataType
    sdf_type: str | None = None
    nullable: bool = True
    const: Any | None = None
    default: Any | None = None
    choices: dict[str, Data] | None = Field(None, alias="sdfChoice")

    def _get_base_schema(self) -> core_schema.CoreSchema:
        """Implemented by sub-classes."""
        raise NotImplementedError

    def get_pydantic_schema(self) -> core_schema.CoreSchema:
        """Get the Pydantic schema for this data quality."""
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

    def validate(self, input: Any) -> Any:
        """Validate and coerce a value."""
        return SchemaValidator(self.get_pydantic_schema()).validate_python(input)


class NumberData(DataQualities):
    type: Literal[DataType.NUMBER]
    unit: str | None = None
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None
    multiple_of: float | None = None
    format: str | None = None
    const: float | None = None
    default: float | None = None

    @model_validator(mode="before")
    @classmethod
    def set_default_type(cls, data: Any):
        if isinstance(data, dict):
            data.setdefault("type", DataType.NUMBER)
        return data

    def _get_base_schema(self) -> core_schema.FloatSchema:
        return core_schema.float_schema(
            ge=self.minimum,
            le=self.maximum,
            gt=self.exclusive_minimum,
            lt=self.exclusive_maximum,
            multiple_of=self.multiple_of,
        )

    def validate(self, input: Any) -> int:
        return super().validate(input)


class IntegerData(DataQualities):
    type: Literal[DataType.INTEGER]
    unit: str | None = None
    minimum: int | None = None
    maximum: int | None = None
    exclusive_minimum: int | None = None
    exclusive_maximum: int | None = None
    multiple_of: int | None = None
    format: str | None = None
    choices: dict[str, IntegerData] | None = Field(None, alias="sdfChoice")
    const: int | None = None
    default: int | None = None

    @model_validator(mode="before")
    @classmethod
    def set_default_type(cls, data: Any):
        if isinstance(data, dict):
            data.setdefault("type", DataType.INTEGER)
        return data

    def _get_base_schema(self) -> core_schema.IntSchema:
        return core_schema.int_schema(
            ge=self.minimum,
            le=self.maximum,
            gt=self.exclusive_minimum,
            lt=self.exclusive_maximum,
            multiple_of=self.multiple_of,
        )

    def validate(self, input: Any) -> int:
        return super().validate(input)


class BooleanData(DataQualities):
    type: Literal[DataType.BOOLEAN]
    const: bool | None = None
    default: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def set_default_type(cls, data: Any):
        if isinstance(data, dict):
            data.setdefault("type", DataType.BOOLEAN)
        return data

    def _get_base_schema(self) -> core_schema.BoolSchema:
        return core_schema.bool_schema()

    def validate(self, input: Any) -> bool:
        return super().validate(input)


class StringData(DataQualities):
    type: Literal[DataType.STRING]
    enum: list[str] | None = None
    min_length: NonNegativeInt = 0
    max_length: NonNegativeInt | None = None
    pattern: str | None = None
    format: str | None = None
    content_format: str | None = None
    choices: dict[str, StringData] | None = Field(None, alias="sdfChoice")
    const: str | None = None
    default: str | None = None

    @model_validator(mode="before")
    @classmethod
    def set_default_type(cls, data: Any):
        if isinstance(data, dict):
            data.setdefault("type", DataType.STRING)
        return data

    def _get_base_schema(
        self,
    ) -> core_schema.StringSchema | core_schema.BytesSchema | core_schema.LiteralSchema:
        if self.enum is not None:
            return core_schema.literal_schema(self.enum)
        if self.sdf_type == "byte-string":
            return core_schema.bytes_schema(
                min_length=self.min_length, max_length=self.max_length
            )
        return core_schema.str_schema(
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
        )

    def validate(self, input: Any) -> str | bytes:
        return super().validate(input)


class ArrayData(DataQualities):
    type: Literal[DataType.ARRAY]
    min_items: NonNegativeInt = 0
    max_items: NonNegativeInt | None = None
    unique_items: bool = False
    items: Data | None = None
    const: list | None = None
    default: list | None = None

    @model_validator(mode="before")
    @classmethod
    def set_default_type(cls, data: Any):
        if isinstance(data, dict):
            data.setdefault("type", DataType.ARRAY)
        return data

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

    def validate(self, input: Any) -> list | set:
        return super().validate(input)


class ObjectData(DataQualities):
    type: Literal[DataType.OBJECT]
    required: list[str] | None = None
    properties: dict[str, Data] | None = None
    const: dict[str, Any] | None = None
    default: dict[str, Any] | None = None

    @model_validator(mode="before")
    @classmethod
    def set_default_type(cls, data: Any):
        if isinstance(data, dict):
            data.setdefault("type", DataType.OBJECT)
        return data

    def _get_base_schema(self) -> core_schema.TypedDictSchema:
        required = self.required or []
        fields = {
            name: core_schema.typed_dict_field(
                property.get_pydantic_schema(), required=name in required
            )
            for name, property in self.properties.items()
        }
        return core_schema.typed_dict_schema(fields)

    def validate(self, input: Any) -> dict:
        return super().validate(input)


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
