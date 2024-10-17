from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CommonQualities(BaseModel):
    model_config = ConfigDict(
        extra="allow", alias_generator=to_camel, populate_by_name=True
    )

    label: str | None = Field(None, validation_alias="title")
    description: str | None = None
    ref: str | None = Field(None, alias="sdfRef", validation_alias="$ref")
