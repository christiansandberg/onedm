import json
from pathlib import Path
from typing import Any
from onedm import sdf


def validate_doc(document: dict, registry: sdf.Registry, check_refs: bool = False):
    resolver = sdf.Resolver(document, registry)
    resolved = resolver.resolve(document)
    if check_refs:
        check_for_refs(resolved, "#")
    sdf.Document.model_validate(resolved)


def validate_file(path: Path, models: Path | None = None, check_refs: bool = False):
    registry = (
        sdf.registry.FileBasedRegistry(models)
        if models
        else sdf.registry.NullRegistry()
    )
    with path.open("r") as fp:
        document = json.load(fp)
    validate_doc(document, registry, check_refs)


def check_for_refs(definition: dict[str, Any], path: str):
    assert (
        "sdfRef" not in definition
    ), f"Unresolved sdfRef {definition['sdfRef']} found in {path}"

    for name, child in definition.items():
        if isinstance(child, dict):
            check_for_refs(child, path + "/" + name)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate an SDF document")
    parser.add_argument("filename", type=Path)
    parser.add_argument("--models", type=Path, help="Directory with global models")
    parser.add_argument(
        "--check-refs",
        action="store_true",
        default=False,
        help="Check that all references could be resolved",
    )

    args = parser.parse_args()
    validate_file(args.filename, args.models, args.check_refs)
