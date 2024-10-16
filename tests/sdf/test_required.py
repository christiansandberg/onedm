from onedm import sdf


def test_required_as_list():
    test = sdf.Object.model_validate(
        {
            "sdfProperty": {
                "prop1": {},
                "prop2": {},
            },
            "sdfRequired": ["prop1"],
        }
    )
    assert "prop1" in test.sdf_required


def test_required_as_prop():
    test = sdf.Object.model_validate(
        {
            "sdfProperty": {
                "prop1": {
                    "type": "integer",
                    "sdfRequired": [True],
                },
                "prop2": {},
            },
        }
    )
    assert test.properties["prop1"].sdf_required
