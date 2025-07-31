from abc import ABC, abstractmethod
from typing import Any, Iterable


NamespaceURI = str
Definition = dict[str, Any]


class Registry(ABC):
    """Model registry interface"""

    @abstractmethod
    def get_models(self, ns: NamespaceURI) -> Iterable[dict]:
        """Get all models for given namespace URI"""
        raise NotImplementedError


class NullRegistry(Registry):
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
        self._db.setdefault(ns, []).append(model)

    def get_models(self, ns: NamespaceURI) -> Iterable[dict]:
        return self._db.get(ns, [])
