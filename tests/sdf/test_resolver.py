from onedm import sdf
import onedm.sdf.registry


def test_multi_level_sdf_ref():
    top_level_doc = {
        "namespace": {
            "example2": "https://example.com/example2",
        },
        "sdfProperty": {
            "example_object": {
                # Does not reference anything by itself
                "type": "object",
                "properties": {
                    "integer": {
                        # Contains a property referencing a local definition
                        "sdfRef": "#/sdfData/Example3",
                        # Remove minimum
                        "minimum": None,
                        # Override maximum
                        "maximum": 42,
                    }
                }
            }
        },
        "sdfData": {
            "Example3": {
                # References a definition in a global namespace
                "sdfRef": "example2:#/sdfData/Example2",
            }
        },
    }

    example2 = {
        "namespace": {
            "example1": "https://example.com/example1",
            "example2": "https://example.com/example2",
        },
        "defaultNamespace": "example2",
        "sdfData": {
            "Example2": {
                # This just references another namespace
                "sdfRef": "example1:#/sdfData/Example1",
                # And overrides the max value
                "maximum": 12,
            }
        },
    }

    example1_a = {
        "namespace": {
            "example": "https://example.com/example1",
        },
        "defaultNamespace": "example",
        "sdfData": {
            "Example1": {
                "type": "integer",
                "minimum": 0,
                "maximum": 10,
                "default": 0,
            }
        },
    }

    # Also contributes to https://example.com/example1, but is empty
    example1_b = {
        "namespace": {
            "example": "https://example.com/example1",
        },
        "defaultNamespace": "example",
        "sdfData": {},
    }

    registry = onedm.sdf.registry.InMemoryRegistry()
    registry.add_model(example2)
    registry.add_model(example1_a)
    registry.add_model(example1_b)

    resolved = sdf.resolve(top_level_doc, registry)
    doc = sdf.Document.model_validate(resolved)

    property = doc.properties["example_object"]
    assert isinstance(property.properties["integer"], sdf.IntegerData)
    assert property.properties["integer"].type == "integer"
    assert property.properties["integer"].minimum is None
    assert property.properties["integer"].maximum == 42
    assert property.properties["integer"].default == 0


def test_pointer_to_nowhere():
    top_level_doc = {
        "sdfData": {
            "Example3": {
                "sdfRef": "#/sdfData/Example2",
            }
        },
    }

    resolved = sdf.resolve(top_level_doc)
    assert resolved == top_level_doc


def test_unresolvable_reference():
    top_level_doc = {
        "namespace": {
            "example": "https://example.com",
        },
        "sdfData": {
            "Example3": {
                "sdfRef": "example:#/sdfData/Example",
            }
        },
    }

    resolved = sdf.resolve(top_level_doc)
    doc = sdf.Document.model_validate(resolved)

    assert doc.data["Example3"].ref == "example:#/sdfData/Example"
