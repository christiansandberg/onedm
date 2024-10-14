"""Loading of SDF files

Extensions supported compared to standard:

* Relative URI references

Takes care of dereferencing.
"""

import io
import json
import urllib.parse
from typing import Any

from .document import Document


class SDFLoader:

    def __init__(self) -> None:
        self.url = ""
        self.root: dict[str, Any] = {}
        self._namespaces: dict[str, SDFLoader] = {}

    def load_file(self, path):
        self.url = str(path)
        with open(path, "r") as fp:
            self.load_from_fp(fp)

    def load_from_fp(self, fp: io.TextIOBase):
        self.root = json.load(fp)
        self._dereference(self.root)

    def load_from_dict(self, doc: dict, url: str = ""):
        self.url = url
        self.root = doc
        self._dereference(self.root)

    def load(self, url: str):
        result = urllib.parse.urlparse(url)
        if not result.scheme:
            self.load_file(url)
        else:
            raise NotImplementedError("Not supported yet")

    def to_sdf(self) -> Document:
        return Document.model_validate(self.root)

    def _dereference(self, definition: dict[str, Any]) -> dict[str, Any]:
        if "sdfRef" in definition:
            # This reference will be used to patch the referenced original
            patch = definition.copy()
            ref: str = patch.pop("sdfRef")

            if ":" in ref:
                # Resolve namespaces
                namespace, path = ref.split(":")
                # Check if this namespace has already been loaded
                if namespace in self._namespaces:
                    ref_root = self._namespaces[namespace].root
                else:
                    # Extension to standard, support relative URIs in namespaces
                    ref_url = urllib.parse.urljoin(
                        self.url, self.root["namespace"][namespace]
                    )
                    loader = SDFLoader()
                    loader.load(ref_url)
                    # Cache the loaded namespace
                    self._namespaces[namespace] = loader

                    ref_root = loader.root
                    ref_url = urllib.parse.urljoin(ref_url, path)
            else:
                ref_url = urllib.parse.urljoin(self.url, ref)
                ref_root = self.root

            result = urllib.parse.urlparse(ref_url)

            fragments = result.fragment.split("/")
            # Traverse down the local tree
            original = ref_root
            for fragment in fragments[1:]:
                if fragment not in original:
                    raise ValueError(f"Could not find {fragment} in {result.geturl()}")
                original = original[fragment]

            if patch:
                # TODO: Do proper JSON Merge Patch (RFC 7396)
                definition = {**original, **patch}
            else:
                # Nothing to patch
                definition = original

        # Continue processing children
        for name, value in definition.items():
            if isinstance(value, dict):
                definition[name] = self._dereference(value)

        return definition
