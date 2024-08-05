import pytest
from onedm import sdf


def test_integer_validation(test_model: sdf.SDF):
    assert test_model.data["Integer"].validate(2) == 2
    with pytest.raises(ValueError):
        test_model.data["Integer"].validate(True)
    # Out of range
    with pytest.raises(ValueError):
        test_model.data["Integer"].validate(3)


def test_number_validation(test_model: sdf.SDF):
    assert test_model.data["Number"].validate(0.5) == 0.5
    assert test_model.data["Number"].validate(1) == 1.0

    # Out of range
    with pytest.raises(ValueError):
        test_model.data["Number"].validate(100)
    # Invalid type (array)
    with pytest.raises(ValueError):
        test_model.data["Number"].validate([1.0])
    # Invalid type (string)
    with pytest.raises(ValueError):
        test_model.data["Number"].validate("string")
    # Invalid multiple of
    with pytest.raises(ValueError):
        test_model.data["Number"].validate(0.1)


def test_string_validation(test_model: sdf.SDF):
    assert test_model.data["String"].validate("0123456789") == "0123456789"

    # Invalid length
    with pytest.raises(ValueError):
        test_model.data["Number"].validate("too short")
    # Invalid type (array)
    with pytest.raises(ValueError):
        test_model.data["Number"].validate(["0123456789"])


def test_nullable_validation(test_model: sdf.SDF):
    assert test_model.data["NullableInteger"].validate(None) == None

    # Not nullable
    with pytest.raises(ValueError):
        test_model.data["Integer"].validate(None)
