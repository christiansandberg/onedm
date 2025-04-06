from onedm import sdf


def test_document_generation():
    doc = sdf.Document(
        info=sdf.Information(
            title="Test title",
        ),
        things={
            "MyThing": sdf.Thing(
                things={
                    "MySubThing": sdf.Thing(
                        objects={
                            "MyObject": sdf.Object(
                                properties={
                                    "MyProperty": sdf.ArrayProperty(
                                        items=sdf.AnyData(
                                            ref="#/sdfData/MyEnum",
                                            # Put a temporary definition here
                                        ),
                                    )
                                }
                            )
                        }
                    )
                }
            )
        },
        data={
            "MyEnum": sdf.IntegerData(
                choices={
                    "ONE": sdf.IntegerData(
                        const=1
                    )
                }
            )
        }
    )

    dump_witout_defaults = doc.model_dump(mode="json", by_alias=True, exclude_defaults=True)
    dump_witout_unset = doc.model_dump(mode="json", by_alias=True, exclude_unset=True)

    cleaned_doc = {
        "info": {
            "title": "Test title"
        },
        "sdfThing": {
            "MyThing": {
                "sdfThing": {
                    "MySubThing": {
                        "sdfObject": {
                            "MyObject": {
                                "sdfProperty": {
                                    "MyProperty": {
                                        "type": "array",
                                        "items": {
                                            "sdfRef": "#/sdfData/MyEnum"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "sdfData": {
            "MyEnum": {
                "type": "integer",
                "sdfChoice": {
                    "ONE": {
                        "type": "integer",
                        "const": 1
                    }
                }
            }
        }
    }

    assert dump_witout_defaults == cleaned_doc
    assert dump_witout_unset == cleaned_doc
