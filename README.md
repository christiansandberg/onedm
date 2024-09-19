# OneDM Python library

This Python package is an early work-in-progress to simplify working with
[One Data Model](https://onedm.org/) in Python.

Since OneDM is in early stages, this library intends to follow the progress
as best as it can and should hence be considered unstable.


## SDF

Currently it supports limited loading and generation of
[SDF](https://ietf-wg-asdf.github.io/SDF/sdf.html) documents.

> The Semantic Definition Format (SDF) is a format for domain experts to use in
> the creation and maintenance of data and interaction models that describe Things,
> i.e., physical objects that are available for interaction over a network.
> An SDF specification describes definitions of SDF Objects/SDF Things and their
> associated interactions (Events, Actions, Properties), as well as the Data types
> for the information exchanged in those interactions.

This library uses [Pydantic](https://docs.pydantic.dev/) to parse, validate,
and dump model descriptions. The Pydantic models enforce a stricter validation
than the current SDF JSON schema where each data type has its own schema.

You can also validate input values against your data definitions.


## Examples

Loading an existing SDF document:

```
>>> from onedm import sdf

>>> loader = sdf.SDFLoader()
>>> loader.load_file("tests/sdf/test.sdf.json")
>>> doc = loader.to_sdf()

>>> doc.info.title        
'Example document for SDF (Semantic Definition Format)'

>>> doc.properties["IntegerProperty"] 
IntegerProperty(observable=True, readable=True, writable=True, label='Example integer', description=None, ref=None, required=[], type=<DataType.INTEGER: 'integer'>, sdf_type=None, nullable=True, const=2, unit=None, minimum=-2, maximum=2, exclusive_minimum=None, exclusive_maximum=None, multiple_of=2, format=None, choices=None, default=None)

>>> doc.data["Integer"].validate_input(3)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "onedm\sdf\data.py", line 129, in validate_input
    return super().validate_input(input)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "onedm\sdf\data.py", line 64, in validate_input
    return SchemaValidator(self.get_pydantic_schema()).validate_python(input)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for constrained-int
  Input should be a multiple of 2 [type=multiple_of, input_value=3, input_type=int]
    For further information visit https://errors.pydantic.dev/2.8/v/multiple_of
```

Creating a new document:

```
>>> from onedm import sdf

>>> doc = sdf.SDF()

>>> doc.info.title = "Generic switch document"
>>> doc.things["switch"] = sdf.Thing(label="Generic switch")
>>> doc.things["switch"].actions["on"] = sdf.Action(label="Turn on")
>>> print(doc.to_json())
{
  "info": {
    "title": "Generic switch document"
  },
  "sdfThing": {
    "switch": {
      "label": "Generic switch",
      "sdfAction": {
        "on": {
          "label": "Turn on"
        }
      }
    }
  }
}
```
