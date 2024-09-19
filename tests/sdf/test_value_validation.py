import pytest
from onedm import sdf


def test_integer_validation():
    integer = sdf.IntegerData(maximum=2)
    assert integer.validate_input(2) == 2
    with pytest.raises(ValueError):
        integer.validate_input(1.5)
    # Out of range
    with pytest.raises(ValueError):
        integer.validate_input(3)


def test_number_validation(test_model: sdf.SDF):
    assert test_model.data["Number"].validate_input(0.5) == 0.5
    assert test_model.data["Number"].validate_input(1) == 1.0

    # Out of range
    with pytest.raises(ValueError):
        test_model.data["Number"].validate_input(100)
    # Invalid type (array)
    with pytest.raises(ValueError):
        test_model.data["Number"].validate_input([1.0])
    # Invalid type (string)
    with pytest.raises(ValueError):
        test_model.data["Number"].validate_input("string")
    # Invalid multiple of
    with pytest.raises(ValueError):
        test_model.data["Number"].validate_input(0.1)


def test_string_validation(test_model: sdf.SDF):
    assert test_model.data["String"].validate_input("0123456789") == "0123456789"

    # Invalid length
    with pytest.raises(ValueError):
        test_model.data["Number"].validate_input("too short")
    # Invalid type (array)
    with pytest.raises(ValueError):
        test_model.data["Number"].validate_input(["0123456789"])


def test_nullable_validation():
    nullable_integer = sdf.IntegerData(nullable=True)
    assert nullable_integer.validate_input(None) == None


def test_non_nullable_validation():
    integer = sdf.IntegerData(nullable=False)
    with pytest.raises(ValueError):
        integer.validate_input(None)
