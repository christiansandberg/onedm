from __future__ import annotations

from typing import Annotated, Literal, Tuple, Union

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
    sdf_required: Tuple[Literal[True]] | None = None


class IntegerProperty(IntegerData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    sdf_required: Tuple[Literal[True]] | None = None


class BooleanProperty(BooleanData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    sdf_required: Tuple[Literal[True]] | None = None


class StringProperty(StringData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    sdf_required: Tuple[Literal[True]] | None = None


class ArrayProperty(ArrayData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    sdf_required: Tuple[Literal[True]] | None = None


class ObjectProperty(ObjectData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    sdf_required: Tuple[Literal[True]] | None = None


class AnyProperty(AnyData):
    observable: bool = True
    readable: bool = True
    writable: bool = True
    sdf_required: Tuple[Literal[True]] | None = None


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

Properties = Annotated[
    dict[str, Property],
    Field(
        default_factory=dict,
        alias="sdfProperty",
        description="Elements of state within Things",
    ),
]


class Action(CommonQualities):
    input_data: Data | None = Field(None, alias="sdfInputData")
    output_data: Data | None = Field(None, alias="sdfOutputData")
    sdf_required: Tuple[Literal[True]] | None = None


Actions = Annotated[
    dict[str, Action],
    Field(
        default_factory=dict,
        alias="sdfAction",
        description="Commands and methods which are invoked",
    ),
]


class Event(CommonQualities):
    output_data: Data | None = Field(None, alias="sdfOutputData")
    sdf_required: Tuple[Literal[True]] | None = None


Events = Annotated[
    dict[str, Event],
    Field(
        default_factory=dict,
        alias="sdfEvent",
        description='"Happenings" associated with a Thing',
    ),
]


DataDefinitions = Annotated[
    dict[str, Data],
    Field(
        default_factory=dict,
        alias="sdfData",
        description=(
            "Common modeling patterns, data constraints, "
            "and semantic anchor concepts"
        ),
    ),
]


class Object(CommonQualities):
    properties: Properties
    actions: Actions
    events: Events
    data: DataDefinitions
    sdf_required: list[str | Literal[True]] = Field(default_factory=list)
    # If array of objects
    min_items: NonNegativeInt | None = None
    max_items: NonNegativeInt | None = None


Objects = Annotated[
    dict[str, Object],
    Field(
        default_factory=dict,
        alias="sdfObject",
        description='Main "atom" of reusable semantics for model construction',
    ),
]


class Thing(CommonQualities):
    things: Things
    objects: Objects
    properties: Properties
    actions: Actions
    events: Events
    data: DataDefinitions
    sdf_required: list[str | Literal[True]] = Field(default_factory=list)
    # If array of things
    min_items: NonNegativeInt | None = None
    max_items: NonNegativeInt | None = None


Things = Annotated[
    dict[str, Thing],
    Field(
        default_factory=dict,
        alias="sdfThing",
        description="Definition of models for complex devices",
    ),
]
