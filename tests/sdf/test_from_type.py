from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import enum
from pydantic import Field, BaseModel, PlainSerializer
from typing import Annotated, Literal

from onedm import sdf
from onedm.sdf.from_type import data_from_type, unresolved_data_from_type


def test_integer():
    data = data_from_type(int)

    assert isinstance(data, sdf.IntegerData)
    assert not data.nullable


def test_float():
    data = data_from_type(float)

    assert isinstance(data, sdf.NumberData)
    assert not data.nullable


def test_bool():
    data = data_from_type(bool)

    assert isinstance(data, sdf.BooleanData)
    assert not data.nullable


def test_str():
    data = data_from_type(str)

    assert isinstance(data, sdf.StringData)
    assert not data.nullable


def test_bytes():
    data = data_from_type(bytes)

    assert isinstance(data, sdf.StringData)
    assert data.sdf_type == "byte-string"
    assert not data.nullable


def test_enum():
    class MyEnum(enum.Enum):
        ONE = 1
        TWO = "two"

    data = data_from_type(MyEnum)

    assert isinstance(data, sdf.AnyData)
    assert data.choices["ONE"].const == 1
    assert data.choices["TWO"].const == "two"
    assert not data.nullable

    unresolved, models = unresolved_data_from_type(MyEnum)
    assert unresolved["sdfRef"] == "#/sdfData/MyEnum"
    assert "#/sdfData/MyEnum" in models


def test_int_enum():
    class MyEnum(enum.IntEnum):
        ONE = 1
        TWO = 2

    data = data_from_type(MyEnum)

    assert isinstance(data, sdf.IntegerData)
    assert data.choices["ONE"].const == 1
    assert data.choices["TWO"].const == 2
    assert not data.nullable


def test_str_enum():
    class MyEnum(str, enum.Enum):
        ONE = "one"
        TWO = "two"

    data = data_from_type(MyEnum)

    assert isinstance(data, sdf.StringData)
    assert data.choices["ONE"].const == "one"
    assert data.choices["TWO"].const == "two"
    assert not data.nullable


def test_union():
    data = data_from_type(int | str | None)

    assert len(data.choices) == 2
    assert "int" in data.choices
    assert "str" in data.choices
    assert data.choices["int"].type == "integer"
    assert data.choices["str"].type == "string"
    assert data.nullable


def test_const():
    data = data_from_type(Literal["const"])

    assert data.const == "const"


def test_string_literals():
    data = data_from_type(Literal["one", "two"])

    assert isinstance(data, sdf.StringData)
    assert data.enum == ["one", "two"]
    assert not data.nullable


def test_nullable():
    data = data_from_type(int | None)

    assert isinstance(data, sdf.IntegerData)
    assert data.nullable


def test_none():
    data = data_from_type(None)

    assert data.const is None
    assert "const" in data.model_fields_set


def test_literal_none():
    data = data_from_type(Literal[None])

    assert data.const is None
    assert "const" in data.model_fields_set


def test_list():
    data = data_from_type(list[str])

    assert isinstance(data, sdf.ArrayData)
    assert isinstance(data.items, sdf.StringData)
    assert not data.unique_items
    assert not data.nullable


def test_set():
    data = data_from_type(set[str])

    assert isinstance(data, sdf.ArrayData)
    assert isinstance(data.items, sdf.StringData)
    assert data.unique_items
    assert not data.nullable


def test_model():
    class MyEnum(str, enum.Enum):
        ONE = "one"
        TWO = "two"

    class TestModel(BaseModel):
        with_default: int = 2
        with_alias: Annotated[int, Field(alias="withAlias")] = 0
        optional: float | None = None
        required: bool | None
        enumeration: MyEnum | None = None

    data = data_from_type(TestModel)

    assert isinstance(data, sdf.ObjectData)
    assert not data.nullable
    assert data.required == ["required"]

    assert isinstance(data.properties["with_default"], sdf.IntegerData)
    assert data.properties["with_default"].default == 2
    assert not data.properties["with_default"].nullable

    assert "withAlias" in data.properties

    assert data.properties["required"].nullable
    assert data.properties["optional"].nullable

    assert isinstance(data.properties["enumeration"], sdf.StringData)
    assert data.properties["enumeration"].choices["ONE"].const == "one"
    assert data.properties["enumeration"].choices["TWO"].const == "two"
    assert data.properties["enumeration"].nullable


def test_dataclass():
    @dataclass
    class TestModel:
        with_default: int = 2

    data = data_from_type(TestModel)

    assert isinstance(data, sdf.ObjectData)
    assert not data.nullable

    assert isinstance(data.properties["with_default"], sdf.IntegerData)
    assert data.properties["with_default"].default == 2
    assert not data.properties["with_default"].nullable


def test_recursive_model():
    class TestModel(BaseModel):
        child: TestModel | None = None

    definition, map = unresolved_data_from_type(TestModel)
    assert definition["sdfRef"] == "#/sdfData/TestModel"

    assert "#/sdfData/TestModel" in map
    # References itself
    assert (
        map["#/sdfData/TestModel"]["properties"]["child"]["sdfRef"]
        == "#/sdfData/TestModel"
    )


def test_custom_serializer():
    UnixTime = Annotated[
        datetime,
        PlainSerializer(datetime.timestamp, return_type=float),
        Field(json_schema_extra={"sdfType": "unix-time"}),
    ]

    data = data_from_type(UnixTime)
    assert isinstance(data, sdf.NumberData)
    assert data.sdf_type == "unix-time"


def test_override_fields():
    class MyEnum(enum.IntEnum):
        ONE = 1

    MyEnumWithLabel = Annotated[MyEnum, Field(title="Custom label")]

    definition, data = unresolved_data_from_type(MyEnumWithLabel)
    # Should re-use existing definition of MyEnum
    assert definition["sdfRef"] == "#/sdfData/MyEnum"
    assert definition["label"] == "Custom label"
    assert "#/sdfData/MyEnum" in data


def test_label():
    data = data_from_type(Annotated[int, Field(title="Test title")])

    assert data.label == "Test title"


def test_description():
    data = data_from_type(Annotated[int, Field(description="Description")])

    assert data.description == "Description"


def test_unit():
    data = data_from_type(Annotated[float, Field(json_schema_extra={"unit": "s"})])

    assert data.unit == "s"
