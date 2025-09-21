from __future__ import annotations

import logging
from typing import NamedTuple
from .registry import Registry, Definition, NullRegistry
from . import exceptions


logger = logging.getLogger(__name__)


class DerefResult(NamedTuple):
    definition: Definition
    resolver: Resolver


class Resolver:
    """SDF resolver

    Allows definitions to be resolved and URIs to be dereferenced.
    To be able to dereference local references, a model must be provided.
    To dereference global URIs, a registry must be provided.
    """

    @classmethod
    def from_registry(cls, registry: Registry) -> Resolver:
        """Create a Resolver from a registry alone

        Will only be able to dereference global URIs.
        """
        return cls({}, registry)

    @classmethod
    def from_document(cls, document: dict) -> Resolver:
        """Create a Resolver from a SDF document

        Will only be able to dereference local pointers.
        """
        return cls(document, NullRegistry())

    def __init__(self, document: dict, registry: Registry):
        self._document = document
        self._registry = registry

    def deref(self, uri: str) -> DerefResult:
        """Dereference URI

        The URI must contain both the namespace and fragment identifier.

        :param uri: A local or global reference with short namespace prefix
        :returns: A tuple of an unresolved definition and a resolver object
                  for further resolving it
        """
        ns, path = uri.split("#", maxsplit=1)
        return self._deref_ns_and_path(ns, path)

    def resolve(self, definition: Definition) -> Definition:
        """Resolve a single definition

        :param definition: A definition to be resolved
        :returns: A resolved copy
        """
        if "sdfRef" in definition:
            try:
                unresolved_original, resolver = self._dereference_internal(
                    definition["sdfRef"]
                )
            except exceptions.PointerToNowhereError as exc:
                logger.warning("%s", exc)
                original = {}
                patch = definition
            else:
                original = resolver.resolve(unresolved_original)
                patch = definition.copy()
                del patch["sdfRef"]
        else:
            original = {}
            patch = definition

        if not patch:
            return original

        self._merge(original, patch)
        return original

    def _dereference_internal(self, ref: str) -> DerefResult:
        if ":" in ref:
            # Reference to a global namespace
            ns_prefix, path = ref.split(":#", maxsplit=1)
            ns = self._document["namespace"][ns_prefix]
        else:
            # Reference to a local definition
            path = ref
            ns = ""

        return self._deref_ns_and_path(ns, path)

    def _deref_ns_and_path(self, ns: str, path: str) -> DerefResult:
        models = self._registry.get_models(ns) if ns else [self._document]

        # Go through the models that may contain a matching path
        for model in models:
            # Start at the root of the model
            definition: Definition = model
            try:
                for segment in path.split("/")[1:]:
                    if not isinstance(definition, dict):
                        raise TypeError(f"{segment} in {ns}#{path} is not an object")
                    definition = definition[segment]
                return DerefResult(definition, Resolver(model, self._registry))
            except KeyError:
                pass

        raise exceptions.PointerToNowhereError(f"Could not find {ns}{path}")

    def _merge(self, original: dict, patch: dict) -> None:
        # Recursive merge patch
        for name, value in patch.items():
            if isinstance(value, dict):
                # May contain further references
                original[name] = self.resolve(value)
            elif value is None and name in original:
                # Deleted
                del original[name]
            else:
                # Added or replaced
                original[name] = value
