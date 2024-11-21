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

    # Enum should be referenced
    assert data.ref == "#/sdfData/MyEnum"
    assert "MyEnum" in data.definitions
    my_enum = data.definitions["MyEnum"]

    assert isinstance(my_enum, sdf.AnyData)
    assert my_enum.choices["ONE"].const == 1
    assert my_enum.choices["TWO"].const == "two"
    assert not data.nullable


def test_int_enum():
    class MyEnum(enum.IntEnum):
        ONE = 1
        TWO = 2

    data = data_from_type(MyEnum)

    # Model should be referenced
    assert data.ref == "#/sdfData/MyEnum"
    assert "MyEnum" in data.definitions
    my_enum = data.definitions["MyEnum"]

    assert isinstance(my_enum, sdf.IntegerData)
    assert my_enum.choices["ONE"].const == 1
    assert my_enum.choices["TWO"].const == 2
    assert not data.nullable


def test_str_enum():
    class MyEnum(str, enum.Enum):
        ONE = "one"
        TWO = "two"

    data = data_from_type(MyEnum)

    # Model should be referenced
    assert data.ref == "#/sdfData/MyEnum"
    assert "MyEnum" in data.definitions
    my_enum = data.definitions["MyEnum"]

    assert isinstance(my_enum, sdf.StringData)
    assert my_enum.choices["ONE"].const == "one"
    assert my_enum.choices["TWO"].const == "two"
    assert not data.nullable


def test_union():
    data = data_from_type(int | str)

    assert len(data.choices) == 2
    assert "choice-1" in data.choices
    assert "choice-2" in data.choices
    assert data.choices["choice-1"].type == "integer"
    assert data.choices["choice-2"].type == "string"


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

    # Model should be referenced
    assert data.ref == "#/sdfData/TestModel"
    assert "TestModel" in data.definitions
    test_model = data.definitions["TestModel"]

    assert isinstance(test_model, sdf.ObjectData)
    assert not data.nullable
    assert test_model.required == ["required"]

    assert isinstance(test_model.properties["with_default"], sdf.IntegerData)
    assert test_model.properties["with_default"].default == 2
    assert not test_model.properties["with_default"].nullable

    assert "withAlias" in test_model.properties

    assert test_model.properties["required"].nullable
    assert test_model.properties["optional"].nullable


def test_dataclass():
    @dataclass
    class TestModel:
        with_default: int = 2

    data = data_from_type(TestModel)

    # Model should be referenced
    assert data.ref == "#/sdfData/TestModel"
    assert "TestModel" in data.definitions
    test_model = data.definitions["TestModel"]

    assert isinstance(test_model, sdf.ObjectData)
    assert not data.nullable

    assert isinstance(test_model.properties["with_default"], sdf.IntegerData)
    assert test_model.properties["with_default"].default == 2
    assert not test_model.properties["with_default"].nullable


def test_label():
    data = data_from_type(Annotated[int, Field(title="Test title")])

    assert data.label == "Test title"


def test_description():
    data = data_from_type(Annotated[int, Field(description="Description")])

    assert data.description == "Description"


def test_unit():
    data = data_from_type(Annotated[float, Field(json_schema_extra={"unit": "s"})])

    assert data.unit == "s"


def test_document():
    doc = sdf.Document()

    @dataclass
    class TestModel:
        with_default: int = 2

    data = data_from_type(TestModel)
    doc.things["thing"] = sdf.Thing()
    doc.things["thing"].objects["object"] = sdf.Object()
    doc.things["thing"].objects["object"].properties["prop"] = (
        sdf.definitions.property_from_data(data)
    )

    dump = doc.model_dump(by_alias=True)
    assert (
        dump["sdfThing"]["thing"]["sdfObject"]["object"]["sdfProperty"]["prop"][
            "sdfRef"
        ]
        == "#/sdfData/TestModel"
    )
    assert "TestModel" in dump["sdfData"]
