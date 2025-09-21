from abc import ABC, abstractmethod
import bisect
import json
from pathlib import Path
from typing import Any, Iterable


NamespaceURI = str
Definition = dict[str, Any]


class Registry(ABC):  # pylint: disable=too-few-public-methods
    """Model registry interface"""

    @abstractmethod
    def get_models(self, ns: NamespaceURI) -> Iterable[dict]:
        """Get all models for given namespace URI

        The models should be sorted by version in reverse order.
        """
        raise NotImplementedError


class NullRegistry(Registry):  # pylint: disable=too-few-public-methods
    """A registry with no models"""

    def get_models(self, _: NamespaceURI) -> Iterable[dict]:
        return []


class InMemoryRegistry(Registry):
    """A registry with pre-loaded models"""

    def __init__(self) -> None:
        self._db: dict[NamespaceURI, list[dict]] = {}

    def add_model(self, model: dict) -> None:
        """Add a model"""
        assert "defaultNamespace" in model, "Model must have a defaultNamespace"
        ns: NamespaceURI = model["namespace"][model["defaultNamespace"]]
        models = self._db.setdefault(ns, [])
        bisect.insort_left(models, model, key=_get_version_from_model)

    def get_models(self, ns: NamespaceURI) -> Iterable[dict]:
        return reversed(self._db.get(ns, []))


class FileBasedRegistry(Registry):
    """A registry based on files in a directory

    The directory is recursively scanned for files with .sdf.json extension.
    The file is parsed and the namespace and version is used to build an
    internal lookup.
    The parsed models are discarded and will be loaded on demand when
    get_models() is called, making it suitable for directories with many files.
    """

    def __init__(self, models_dir: Path | str) -> None:
        self._dir = Path(models_dir)
        self._lookup: dict[NamespaceURI, list[Path]] = {}
        self.update()

    def update(self) -> None:
        """Scan directory for models"""
        self._lookup = {}
        version_lookup: dict[NamespaceURI, list[str]] = {}

        # Populate lookup
        for path in self._dir.rglob("*.sdf.json"):
            model = self._get_model_from_path(path)
            if "defaultNamespace" not in model:
                # Skip models that don't contribute to a namespace
                continue

            ns: NamespaceURI = model["namespace"][model["defaultNamespace"]]
            version = _get_version_from_model(model)
            models = self._lookup.setdefault(ns, [])
            versions = version_lookup.setdefault(ns, [])
            pos = bisect.bisect_left(versions, version)
            models.insert(pos, path)
            versions.insert(pos, version)

    @staticmethod
    def _get_model_from_path(path: Path) -> dict:
        with path.open("r") as fp:
            return json.load(fp)

    def get_models(self, ns: NamespaceURI) -> Iterable[dict]:
        return map(self._get_model_from_path, reversed(self._lookup.get(ns, [])))


def _get_version_from_model(model: dict) -> str:
    return model.get("info", {}).get("version", "")
