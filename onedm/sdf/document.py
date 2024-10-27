from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_serializer
from pydantic.alias_generators import to_camel

from . import definitions


class Information(BaseModel):
    """Information block

    The information block contains generic metadata for the SDF document itself
    and all included definitions.
    """

    title: Annotated[
        str | None,
        Field(description="A short summary to be displayed in search results, etc."),
    ] = None
    description: Annotated[
        str | None,
        Field(description="Long-form text description (no constraints)"),
    ] = None
    version: Annotated[
        str | None,
        Field(description="The incremental version of the definition"),
    ] = None
    modified: Annotated[
        datetime | None,
        Field(description="Time of the latest modification"),
    ] = None
    copyright: Annotated[
        str | None,
        Field(
            description="Link to text or embedded text containing a copyright notice"
        ),
    ] = None
    license: Annotated[
        str | None,
        Field(description="Link to text or embedded text containing license terms"),
    ] = None
    features: list[str] = Field(
        default_factory=list, description="List of extension features used"
    )


class Document(BaseModel):
    model_config = ConfigDict(
        extra="allow", alias_generator=to_camel, populate_by_name=True
    )

    info: Information = Field(default_factory=Information)
    namespace: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Defines short names mapped to namespace URIs, "
            "to be used as identifier prefixes"
        ),
    )
    default_namespace: Annotated[
        str | None,
        Field(
            description=(
                "Identifies one of the prefixes in the namespace map "
                "to be used as a default in resolving identifiers"
            ),
        ),
    ] = None
    things: dict[str, definitions.Thing] = Field(
        default_factory=dict,
        alias="sdfThing",
        description="Definition of models for complex devices",
    )
    objects: dict[str, definitions.Object] = Field(
        default_factory=dict,
        alias="sdfObject",
        description='Main "atom" of reusable semantics for model construction',
    )
    properties: dict[str, definitions.Property] = Field(
        default_factory=dict,
        alias="sdfProperty",
        description="Elements of state within Things",
    )
    actions: dict[str, definitions.Action] = Field(
        default_factory=dict,
        alias="sdfAction",
        description="Commands and methods which are invoked",
    )
    events: dict[str, definitions.Event] = Field(
        default_factory=dict,
        alias="sdfEvent",
        description='"Happenings" associated with a Thing',
    )
    data: dict[str, definitions.Data] = Field(
        default_factory=dict,
        alias="sdfData",
        description=(
            "Common modeling patterns, data constraints, "
            "and semantic anchor concepts"
        ),
    )

    def to_json(self) -> str:
        return self.model_dump_json(indent=2, exclude_defaults=True, by_alias=True)

    @field_serializer("data", mode="wrap")
    def populate_sdf_data(self, data: dict, nxt):
        """Populate sdfData

        Scans through the whole document looking for $defs and collects them
        in the document's root #/sdfData.
        """
        data = data.copy()

        def update_from_parent(
            parent: Document | definitions.Object | definitions.Thing,
        ):
            for prop in parent.properties.values():
                data.update(prop.definitions)
            for action in parent.actions.values():
                if action.input_data:
                    data.update(action.input_data.definitions)
                if action.output_data:
                    data.update(action.output_data.definitions)
            for event in parent.events.values():
                if event.output_data:
                    data.update(event.output_data.definitions)

            if isinstance(parent, definitions.Thing):
                for thing in parent.things.values():
                    update_from_parent(thing)
                for obj in parent.objects.values():
                    update_from_parent(obj)

        update_from_parent(self)
        for thing in self.things.values():  # pylint: disable=no-member
            update_from_parent(thing)

        return nxt(data)

    @model_serializer(mode="wrap")
    def remove_definitions(self, nxt):
        """Remove $ref and $defs

        These are temporary entries created by Pydantic.
        """
        doc = nxt(self)
        remove_definitions(doc)
        return doc


def remove_definitions(obj: dict[str, Any]):
    for key, value in list(obj.items()):
        if key == "$defs":
            del obj[key]
        if isinstance(value, dict):
            remove_definitions(value)
