from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CommonQualities(BaseModel):
    model_config = ConfigDict(extra="allow", alias_generator=to_camel)

    label: str | None = None
    description: str | None = None
    ref: Annotated[str | None, Field(alias="sdfRef")] = None

    def get_extra(self) -> dict[str, Any]:
        return self.__pydantic_extra__ if self.__pydantic_extra__ is not None else {}
