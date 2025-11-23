from __future__ import annotations

from typing import Annotated, Literal, Tuple, Union

from pydantic import Field, NonNegativeInt, TypeAdapter

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


class PropertyBase:  # pylint: disable=too-few-public-methods
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


# pylint: disable-next=invalid-name
PropertyAdapter: TypeAdapter[Property] = TypeAdapter(Property)


def property_from_data(data: Data) -> Property:
    return PropertyAdapter.validate_python(data.model_dump())


class Action(CommonQualities):
    input_data: Annotated[Data | None, Field(alias="sdfInputData")] = None
    output_data: Annotated[Data | None, Field(None, alias="sdfOutputData")] = None
    sdf_required: Tuple[Literal[True]] | None = None


class Event(CommonQualities):
    output_data: Annotated[Data | None, Field(None, alias="sdfOutputData")] = None
    sdf_required: Tuple[Literal[True]] | None = None


class Object(CommonQualities):
    properties: dict[str, Property] = Field(
        default_factory=dict,
        alias="sdfProperty",
        description="Elements of state within Things",
    )
    actions: dict[str, Action] = Field(
        default_factory=dict,
        alias="sdfAction",
        description="Commands and methods which are invoked",
    )
    events: dict[str, Event] = Field(
        default_factory=dict,
        alias="sdfEvent",
        description='"Happenings" associated with a Thing',
    )
    data: dict[str, Data] = Field(
        default_factory=dict,
        alias="sdfData",
        description=(
            "Common modeling patterns, data constraints, "
            "and semantic anchor concepts"
        ),
    )
    context: dict[str, Data] = Field(
        default_factory=dict,
        alias="sdfContext",
        description="Static, descriptive, and non-interactive metadata",
    )
    sdf_required: list[str | Literal[True]] = Field(default_factory=list)
    # If array of objects
    min_items: NonNegativeInt | None = None
    max_items: NonNegativeInt | None = None


class Thing(CommonQualities):
    things: dict[str, Thing] = Field(
        default_factory=dict,
        alias="sdfThing",
        description="Definition of models for complex devices",
    )
    objects: dict[str, Object] = Field(
        default_factory=dict,
        alias="sdfObject",
        description='Main "atom" of reusable semantics for model construction',
    )
    properties: dict[str, Property] = Field(
        default_factory=dict,
        alias="sdfProperty",
        description="Elements of state within Things",
    )
    actions: dict[str, Action] = Field(
        default_factory=dict,
        alias="sdfAction",
        description="Commands and methods which are invoked",
    )
    events: dict[str, Event] = Field(
        default_factory=dict,
        alias="sdfEvent",
        description='"Happenings" associated with a Thing',
    )
    data: dict[str, Data] = Field(
        default_factory=dict,
        alias="sdfData",
        description=(
            "Common modeling patterns, data constraints, "
            "and semantic anchor concepts"
        ),
    )
    context: dict[str, Data] = Field(
        default_factory=dict,
        alias="sdfContext",
        description="Static, descriptive, and non-interactive metadata",
    )
    sdf_required: list[str | Literal[True]] = Field(default_factory=list)
    # If array of things
    min_items: NonNegativeInt | None = None
    max_items: NonNegativeInt | None = None


Thing.model_rebuild()
