from __future__ import annotations

from typing import Annotated, Literal, Tuple, Union

from pydantic import Field, NonNegativeInt, TypeAdapter

from .common import CommonQualities
from .data import (
    AnyData,
    ArrayData,
    BooleanData,
    Data,
    DataDefinitions,
    IntegerData,
    NumberData,
    ObjectData,
    StringData,
)


class PropertyBase:
    observable: bool = True
    readable: bool = True
    writable: bool = True
    sdf_required: Tuple[Literal[True]] | None = None


class NumberProperty(NumberData, PropertyBase):
    pass


class IntegerProperty(IntegerData, PropertyBase):
    pass


class BooleanProperty(BooleanData, PropertyBase):
    pass


class StringProperty(StringData, PropertyBase):
    pass


class ArrayProperty(ArrayData, PropertyBase):
    pass


class ObjectProperty(ObjectData, PropertyBase):
    pass


class AnyProperty(AnyData, PropertyBase):
    pass


Property = Union[
    AnyProperty,
    Annotated[
        IntegerProperty
        | NumberProperty
        | BooleanProperty
        | StringProperty
        | ArrayProperty
        | ObjectProperty,
        Field(discriminator="type"),
    ],
]


PropertyAdapter: TypeAdapter[Property] = TypeAdapter(Property)


def property_from_data(data: Data) -> Property:
    return PropertyAdapter.validate_python(data.model_dump())


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
