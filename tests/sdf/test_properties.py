from onedm import sdf


def test_integer_property(test_model: sdf.Document):
    assert isinstance(test_model.properties["IntegerProperty"], sdf.IntegerProperty)
    assert test_model.properties["IntegerProperty"].label == "Example integer"


def test_number_property(test_model: sdf.Document):
    assert isinstance(test_model.properties["NumberProperty"], sdf.NumberProperty)
    assert test_model.properties["NumberProperty"].label == "Example number"


def test_boolean_property(test_model: sdf.Document):
    assert isinstance(test_model.properties["BooleanProperty"], sdf.BooleanProperty)
    assert test_model.properties["BooleanProperty"].label == "Example boolean"


def test_string_property(test_model: sdf.Document):
    assert isinstance(test_model.properties["StringProperty"], sdf.StringProperty)
    assert test_model.properties["StringProperty"].label == "Example string"


def test_array_property(test_model: sdf.Document):
    assert isinstance(test_model.properties["ArrayProperty"], sdf.ArrayProperty)
    assert test_model.properties["ArrayProperty"].label == "Example array"


def test_object_property(test_model: sdf.Document):
    assert isinstance(test_model.properties["ObjectProperty"], sdf.ObjectProperty)
    assert test_model.properties["ObjectProperty"].label == "Example object"


def test_unknown_property(test_model: sdf.Document):
    assert isinstance(test_model.properties["UnknownProperty"], sdf.AnyProperty)
