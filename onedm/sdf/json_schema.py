from pydantic import TypeAdapter

from .data import Data


DataModel = TypeAdapter(Data)


def from_json_schema(definition: dict) -> Data:
    definition = process_node(definition, definition)

    return DataModel.validate_python(definition)


def process_node(definition: dict, root: dict) -> dict:
    if "$ref" in definition:
        ref: str = definition.pop("$ref")
        # Try to dereference for now, in the future we may want to use
        # sdfData to store definitions
        fragments: list[str] = ref.split("/")
        assert fragments[0] == "#", "Only internal references supported"
        referenced = root
        for fragment in fragments[1:]:
            referenced = referenced[fragment]
        definition = {**referenced, **definition}

    if "title" in definition:
        # SDF uses label instead of title
        definition["label"] = definition.pop("title")

    if "anyOf" in definition:
        definition = convert_anyof(definition["anyOf"], root)
    else:
        # Can't be null
        definition["nullable"] = False

    if "enum" in definition:
        # Could maybe be replaced with sdfChoice
        definition = convert_enum(definition)

    if definition.get("format") == "binary":
        definition["sdfType"] = "byte-string"

    if "items" in definition:
        definition["items"] = process_node(definition["items"], root)

    if "properties" in definition:
        for key, value in definition["properties"].items():
            definition["properties"][key] = process_node(value, root)

    if "$defs" in definition:
        # Don't need these anymore
        definition.pop("$defs")

    return definition


def convert_anyof(anyof: list[dict], root) -> dict:
    nullable = False
    for option in anyof:
        option = process_node(option, root)
        if option["type"] == "null":
            # Replace this null option with nullable property
            nullable = True
            anyof.remove(option)
    if len(anyof) > 1:
        # TODO: Use sdfChoice
        raise NotImplementedError("Unions not supported yet")
    # Flatten
    definition = anyof[0]
    definition["nullable"] = nullable
    return definition


def convert_enum(definition: dict) -> dict:
    if len(definition["enum"]) == 1:
        # Probably means its a constant
        definition["const"] = definition["enum"][0]
        del definition["enum"]
    return definition


__all__ = ["from_json_schema"]
