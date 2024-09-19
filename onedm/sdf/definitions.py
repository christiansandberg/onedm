from __future__ import annotations
from typing import Annotated, Literal, Union, Tuple

from pydantic import Field, NonNegativeInt

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


class NumberProperty(NumberData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    required: Tuple[Literal[True]] | None = Field(default=None, alias="sdfRequired")


class IntegerProperty(IntegerData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    required: Tuple[Literal[True]] | None = Field(default=None, alias="sdfRequired")


class BooleanProperty(BooleanData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    required: Tuple[Literal[True]] | None = Field(default=None, alias="sdfRequired")


class StringProperty(StringData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    required: Tuple[Literal[True]] | None = Field(default=None, alias="sdfRequired")


class ArrayProperty(ArrayData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    required: Tuple[Literal[True]] | None = Field(default=None, alias="sdfRequired")


class ObjectProperty(ObjectData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    required: Tuple[Literal[True]] | None = Field(default=None, alias="sdfRequired")


class AnyProperty(AnyData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    required: Tuple[Literal[True]] | None = Field(default=None, alias="sdfRequired")


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
    required: list[str] = Field(default_factory=list, alias="sdfRequired")
    # If array of objects
    min_items: NonNegativeInt | None = None
    max_items: NonNegativeInt | None = None


class Thing(CommonQualities):
    things: dict[str, Thing] = Field(default_factory=dict, alias="sdfThing")
    objects: dict[str, Object] = Field(default_factory=dict, alias="sdfObject")
    properties: dict[str, Property] = Field(default_factory=dict, alias="sdfProperty")
    actions: dict[str, Action] = Field(default_factory=dict, alias="sdfAction")
    events: dict[str, Event] = Field(default_factory=dict, alias="sdfEvent")
    data: dict[str, Data] = Field(default_factory=dict, alias="sdfData")
    required: list[str] = Field(default_factory=list, alias="sdfRequired")
    # If array of things
    min_items: NonNegativeInt | None = None
    max_items: NonNegativeInt | None = None
