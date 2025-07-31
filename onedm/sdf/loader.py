"""Loading of SDF files"""

import io
import json
from typing import Any

from .document import Document
from .registry import NullRegistry
from .resolver import resolve


class SDFLoader:

    def __init__(self) -> None:
        self.root: dict[str, Any] = {}
        self.registry = NullRegistry()

    def load_file(self, path):
        with open(path, "r", encoding="utf-8") as fp:
            self.load_from_fp(fp)

    def load_from_fp(self, fp: io.TextIOBase):
        self.load_from_dict(json.load(fp))

    def load_from_dict(self, doc: dict):
        self.root = resolve(doc, self.registry)

    def to_sdf(self) -> Document:
        return Document.model_validate(self.root)
