import logging
from pathlib import Path
import subprocess

import pytest
from onedm import sdf


@pytest.fixture(scope="session")
def playground(tmp_path_factory: pytest.TempPathFactory):
    tmpdir = tmp_path_factory.mktemp("playground")
    subprocess.run(
        ["git", "clone", "https://github.com/one-data-model/playground.git", tmpdir],
        check=True,
    )
    return tmpdir


def test_parse_all_playground_models(playground: Path):
    IGNORED = [
        # Mixes numbers and integers
        "sdfobject-genericlevel.sdf.json",
    ]

    for path in playground.joinpath("sdfObject").glob("*.sdf.json"):
        if path.name in IGNORED:
            logging.warning("Skipping %s", path.name)
            continue

        loader = sdf.SDFLoader()
        logging.info("Parsing %s", path.name)
        loader.load_file(path)
        doc = loader.to_sdf()

        assert doc.data or doc.objects, f"No sdfData or sdfObject found in {path.name}"


def test_genericonoff(playground: Path):
    loader = sdf.SDFLoader()
    loader.load_file(playground / "sdfObject" / "sdfobject-genericonoff.sdf.json")
    doc = loader.to_sdf()

    assert doc.info.title == "Example Bluetooth mesh Generic OnOff Model"
    assert (
        doc.info.license
        == "https://github.com/one-data-model/oneDM/blob/master/LICENSE"
    )

    on_off = doc.objects["GenericOnOff"].properties["OnOff"]
    assert isinstance(on_off, sdf.AnyProperty)


def test_resolve_uri(playground: Path):
    registry = sdf.registry.FileBasedRegistry(playground)
    resolver = sdf.Resolver.from_registry(registry)
    definition, resolver = resolver.deref("https://onedm.org/ecosystem/ocf#/sdfObject/alarm")
    required, _ = resolver.deref(definition["sdfRequired"][0])
    assert required["description"] == "This Property describes the status of the alarm: true - on, false - off."
