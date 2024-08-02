from datetime import datetime

from pydantic import BaseModel, Field

from .definitions import Data, Event, Object, Property, Thing


class Information(BaseModel):
    title: str | None = None
    version: str | None = None
    copyright: str | None = None
    license: str | None = None
    features: list[str] = Field(default_factory=list)
    modified: datetime | None = None


class SDF(BaseModel):
    info: Information = Field(default_factory=Information)
    namespace: dict[str, str] = Field(default_factory=dict)
    default_namespace: str | None = Field(None, alias="defaultNamespace")
    things: dict[str, Thing] = Field(default_factory=dict, alias="sdfThing")
    objects: dict[str, Object] = Field(default_factory=dict, alias="sdfObject")
    properties: dict[str, Property] = Field(default_factory=dict, alias="sdfProperty")
    events: dict[str, Event] = Field(default_factory=dict, alias="sdfEvent")
    data: dict[str, Data] = Field(default_factory=dict, alias="sdfData")

    def to_json(self) -> str:
        return self.model_dump_json(indent=2, exclude_defaults=True, by_alias=True)
