from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
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
    features: Annotated[
        list[str],
        Field(default_factory=list, description="List of extension features used"),
    ]


class Document(BaseModel):
    model_config = ConfigDict(
        extra="allow", alias_generator=to_camel, populate_by_name=True
    )

    info: Annotated[
        Information,
        Field(default_factory=Information),
    ]
    namespace: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description=(
                "Defines short names mapped to namespace URIs, "
                "to be used as identifier prefixes"
            ),
        ),
    ]
    default_namespace: Annotated[
        str | None,
        Field(
            description=(
                "Identifies one of the prefixes in the namespace map "
                "to be used as a default in resolving identifiers"
            ),
        ),
    ] = None
    things: definitions.Things
    objects: definitions.Objects
    properties: definitions.Properties
    actions: definitions.Actions
    events: definitions.Events
    data: definitions.DataDefinitions

    def to_json(self) -> str:
        return self.model_dump_json(indent=2, exclude_defaults=True, by_alias=True)
