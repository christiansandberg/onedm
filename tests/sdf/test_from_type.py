from dataclasses import dataclass
import enum
from pydantic import Field, BaseModel
from typing import Annotated, Literal

import pytest

from onedm import sdf
from onedm.sdf.from_type import data_from_type


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
    class TestModel(BaseModel):
        with_default: int = 2
        with_alias: Annotated[int, Field(alias="withAlias")] = 0
        optional: float | None = None
        required: bool | None

    data = data_from_type(TestModel)

    assert isinstance(data, sdf.ObjectData)
    assert data.label == "TestModel"
    assert not data.nullable
    assert data.required == ["required"]

    assert isinstance(data.properties["with_default"], sdf.IntegerData)
    assert data.properties["with_default"].default == 2
    assert not data.properties["with_default"].nullable

    assert "withAlias" in data.properties

    assert data.properties["required"].nullable
    assert data.properties["optional"].nullable


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


@pytest.mark.xfail(reason="Not implemented")
def test_label():
    data = data_from_type(Annotated[int, Field(title="Test title")])

    assert data.label == "Test title"


def test_none():
    assert data_from_type(None) is None
