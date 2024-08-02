from pathlib import Path
import pytest

from onedm import sdf


@pytest.fixture(scope="session")
def test_model():
    loader = sdf.SDFLoader()
    loader.load_file(Path(__file__).parent / "test.sdf.json")
    return loader.to_sdf()
