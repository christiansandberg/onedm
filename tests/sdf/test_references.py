from onedm import sdf


def test_reference(test_model: sdf.Document):
    assert isinstance(test_model.data["Reference"], sdf.IntegerData)
    assert test_model.data["Reference"].const == 0
    assert test_model.data["Reference"].maximum == 3
