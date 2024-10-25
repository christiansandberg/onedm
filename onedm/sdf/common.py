from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CommonQualities(BaseModel):
    model_config = ConfigDict(
        extra="allow", alias_generator=to_camel, populate_by_name=True
    )

    label: Annotated[str | None, Field(validation_alias="title")] = None
    description: str | None = None
    ref: Annotated[str | None, Field(alias="sdfRef", validation_alias="$ref")] = None
