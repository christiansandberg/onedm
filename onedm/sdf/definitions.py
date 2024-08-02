from __future__ import annotations
from typing import Annotated, Union

from pydantic import Field

from .common import CommonQualities
from .data import (
    AnyData,
    ArrayData,
    BooleanData,
    Data,
    IntegerData,
    NumberData,
    ObjectData,
    StringData,
)


class PropertyCommon:
    observable: bool = True
    readable: bool = True
    writable: bool = True


class NumberProperty(NumberData, PropertyCommon):
    pass


class IntegerProperty(IntegerData, PropertyCommon):
    pass


class BooleanProperty(BooleanData, PropertyCommon):
    pass


class StringProperty(StringData, PropertyCommon):
    pass


class ArrayProperty(ArrayData, PropertyCommon):
    pass


class ObjectProperty(ObjectData, PropertyCommon):
    pass


class AnyProperty(AnyData, PropertyCommon):
    pass


Property = Union[
    Annotated[
        IntegerProperty
        | NumberProperty
        | BooleanProperty
        | StringProperty
        | ArrayProperty
        | ObjectProperty,
        Field(discriminator="type"),
    ],
    AnyProperty,
]


class Action(CommonQualities):
    input_data: Data | None = Field(None, alias="sdfInputData")
    output_data: Data | None = Field(None, alias="sdfOutputData")


class Event(CommonQualities):
    output_data: Data | None = Field(None, alias="sdfOutputData")


class Object(CommonQualities):
    properties: dict[str, Property] = Field(default_factory=dict, alias="sdfProperty")
    actions: dict[str, Action] = Field(default_factory=dict, alias="sdfAction")
    events: dict[str, Event] = Field(default_factory=dict, alias="sdfEvent")
    data: dict[str, Data] = Field(default_factory=dict, alias="sdfData")
    # If array of objects
    min_items: int | None = None
    max_items: int | None = None


class Thing(CommonQualities):
    things: dict[str, Thing] = Field(default_factory=dict, alias="sdfThing")
    objects: dict[str, Object] = Field(default_factory=dict, alias="sdfObject")
    properties: dict[str, Property] = Field(default_factory=dict, alias="sdfProperty")
    actions: dict[str, Action] = Field(default_factory=dict, alias="sdfAction")
    events: dict[str, Event] = Field(default_factory=dict, alias="sdfEvent")
    data: dict[str, Data] = Field(default_factory=dict, alias="sdfData")
    # If array of things
    min_items: int | None = None
    max_items: int | None = None
