import logging
from .registry import Registry, Definition, NullRegistry
from . import exceptions


logger = logging.getLogger(__name__)


def resolve(model: dict, registry: Registry | None = None) -> dict:
    """Resolve a model

    The provided model or SDF document is scanned for sdfRef references and
    attempts to resolve them, leaving any unresolved references as-is.

    To be able to resolve from global namespaces, a registry must be provided.

    :param model: The model to resolve
    :param registry: A registry to resolve global references with
    """
    return resolve_definition(model, model, registry or NullRegistry())


def resolve_ref(
    ref: str, base_model: dict, registry: Registry
) -> tuple[dict, Definition]:
    if ":" in ref:
        # Reference to a global namespace
        ns_prefix, path = ref.split(":", maxsplit=1)
        ns = base_model["namespace"][ns_prefix]
        # Get a list of all models contributing to this namespace
        models = registry.get_models(ns)
    else:
        # Reference to a local (?) definition
        path = ref
        models = [base_model]
        if "defaultNamespace" in base_model:
            # Local reference or to a model in the same namespace
            ns_prefix = base_model["defaultNamespace"]
            ns = base_model["namespace"][ns_prefix]
            models.extend(registry.get_models(ns))
        else:
            # Can only be resolved by the current model
            ns = ""

    # Go through the models that may contain a matching path
    for model in models:
        # Start at the root of the model
        value = model
        try:
            for segment in path.split("/")[1:]:
                if not isinstance(value, dict):
                    raise TypeError(f"{segment} in {ns}{ref} is not an object")
                value = value[segment]
            return model, value
        except KeyError:
            pass

    raise exceptions.PointerToNowhereError(f"Could not find {ns}{path}")


def resolve_definition(
    definition: Definition, base_model: dict, registry: Registry
) -> Definition:
    """Resolve a single definition

    :param definition: A definition to be resolved
    :param base_model: The model to resolve local references with
    :param registry: A registry to resolve global references with
    """
    if "sdfRef" in definition:
        try:
            ref_model, target = resolve_ref(definition["sdfRef"], base_model, registry)
            patched = resolve_definition(target, ref_model, registry)
        except exceptions.PointerToNowhereError:
            logger.warning("Could not resolve %s", definition["sdfRef"])
            ref_model = base_model
            patched = {}
    else:
        ref_model = base_model
        patched = {}

    merge(patched, definition, base_model, registry)
    return patched


def merge(target: dict, patch: dict, base_model: dict, registry: Registry) -> None:
    # Recursive merge patch
    for name, value in patch.items():
        if isinstance(value, dict):
            # May contain further references
            target[name] = resolve_definition(value, base_model, registry)
        elif value is None and name in target:
            # Deleted
            del target[name]
        else:
            # Added or replaced
            target[name] = value
