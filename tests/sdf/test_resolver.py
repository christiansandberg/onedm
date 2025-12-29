import pytest
from onedm import sdf
import onedm.sdf.exceptions
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
                        # Adds another choice
                        "sdfChoice": {
                            "CHOICE_2": {
                                # A reference embedded inside the patch
                                "sdfRef": "#/sdfData/Integer2",
                            },
                        },
                    }
                }
            }
        },
        "sdfData": {
            "Example3": {
                # References a definition in a global namespace
                "sdfRef": "example2:#/sdfData/Example2",
            },
            "Integer2": {
                "const": 2,
            },
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
                "sdfChoice": {
                    "CHOICE_1": {
                        "const": 1,
                    },
                },
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
    registry.add_document(example2)
    registry.add_document(example1_a)
    registry.add_document(example1_b)

    resolver = sdf.Resolver(top_level_doc, registry)
    resolved = resolver.resolve(top_level_doc)
    doc = sdf.Document.model_validate(resolved)

    property = doc.properties["example_object"]
    assert isinstance(property.properties["integer"], sdf.IntegerData)
    assert property.properties["integer"].type == "integer"
    assert property.properties["integer"].minimum is None
    assert property.properties["integer"].maximum == 42
    assert property.properties["integer"].default == 0
    assert property.properties["integer"].choices["CHOICE_1"].const == 1
    assert property.properties["integer"].choices["CHOICE_2"].const == 2


def test_pointer_to_nowhere():
    top_level_doc = {
        "sdfData": {
            "Example3": {
                "sdfRef": "#/sdfData/Example2",
            }
        },
    }

    resolver = sdf.Resolver.from_document(top_level_doc)
    with pytest.raises(onedm.sdf.exceptions.InvalidLocalReferenceError):
        resolver.resolve(top_level_doc)


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

    resolver = sdf.Resolver.from_document(top_level_doc)
    resolved = resolver.resolve(top_level_doc)
    doc = sdf.Document.model_validate(resolved)

    assert doc.data["Example3"].ref == "example:#/sdfData/Example"
