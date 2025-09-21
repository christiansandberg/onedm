"""Loading of SDF files"""

import io
import json
from typing import Any

from .document import Document
from .registry import Registry, NullRegistry
from .resolver import Resolver


NULL_REGISTRY = NullRegistry()


class SDFLoader:

    def __init__(self, registry: Registry = NULL_REGISTRY) -> None:
        self.root: dict[str, Any] = {}
        self.registry = registry

    def load_file(self, path):
        with open(path, "r", encoding="utf-8") as fp:
            self.load_from_fp(fp)

    def load_from_fp(self, fp: io.TextIOBase):
        self.load_from_dict(json.load(fp))

    def load_from_dict(self, doc: dict):
        self.root = doc

    def to_sdf(self) -> Document:
        doc = Resolver(self.root, self.registry).resolve(self.root)
        return Document.model_validate(doc)
