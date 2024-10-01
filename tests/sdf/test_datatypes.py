from onedm import sdf


def test_integer_data(test_model: sdf.Document):
    assert isinstance(test_model.data["Integer"], sdf.IntegerData)
    assert test_model.data["Integer"].minimum == -2
    assert test_model.data["Integer"].maximum == 2
    assert test_model.data["Integer"].multiple_of == 2


def test_number_data(test_model: sdf.Document):
    assert isinstance(test_model.data["Number"], sdf.NumberData)
    assert test_model.data["Number"].minimum == -1.5
    assert test_model.data["Number"].maximum == 1.5
    assert test_model.data["Number"].multiple_of == 0.5


def test_integer_choices(test_model: sdf.Document):
    assert isinstance(test_model.data["Enum"], sdf.IntegerData)
    assert isinstance(test_model.data["Enum"].choices["One"], sdf.IntegerData)
    assert test_model.data["Enum"].choices["One"].const == 1


def test_boolean_data(test_model: sdf.Document):
    assert isinstance(test_model.data["Boolean"], sdf.BooleanData)
    assert test_model.data["Boolean"].const == True


def test_string_data(test_model: sdf.Document):
    assert isinstance(test_model.data["String"], sdf.StringData)
    assert test_model.data["String"].min_length == 10
    assert test_model.data["String"].max_length == 100
    assert test_model.data["String"].pattern == ".*"


def test_bytestring_data(test_model: sdf.Document):
    assert isinstance(test_model.data["ByteString"], sdf.StringData)
    assert test_model.data["ByteString"].sdf_type == "byte-string"


def test_array_data(test_model: sdf.Document):
    assert isinstance(test_model.data["Array"], sdf.ArrayData)
    assert test_model.data["Array"].min_items == 1
    assert test_model.data["Array"].max_items == 5

    assert isinstance(test_model.data["Array"].items, sdf.IntegerData)


def test_object_data(test_model: sdf.Document):
    assert isinstance(test_model.data["Object"], sdf.ObjectData)

    assert isinstance(test_model.data["Object"].properties["prop1"], sdf.NumberData)
    assert test_model.data["Object"].required == ["prop1"]


def test_unknown_data(test_model: sdf.Document):
    assert isinstance(test_model.data["Unknown"], sdf.AnyData)


def test_serialization_exluding_defaults():
    integer = sdf.IntegerData()
    assert "type" in integer.model_dump(exclude_defaults=True)
