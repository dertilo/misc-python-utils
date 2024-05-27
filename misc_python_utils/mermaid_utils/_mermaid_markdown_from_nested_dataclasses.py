import logging
import uuid
from collections.abc import Iterator
from dataclasses import fields
from typing import Any

from buildable_dataclasses.hashcached_data.hashcached_data import (
    _CREATE_CACHE_DIR_IN_BASE_DIR,
)
from nested_dataclass_serialization.dataclass_serialization_utils import SPECIAL_KEYS

from misc_python_utils.dataclass_utils import _UNDEFINED
from misc_python_utils.mermaid_utils.mermaid_data_models import (
    Dict,
    MermaidNode,
    MermaidTriple,
    NodeDependencies,
)
from misc_python_utils.prefix_suffix import PrefixSuffix

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html

CLASSES_BLACKLIST = [
    _CREATE_CACHE_DIR_IN_BASE_DIR.__name__,
    _UNDEFINED.__name__,
    PrefixSuffix.__name__,
]


def generate_mermaid_triples(
    d: dict,
    set_of_triple_ids: list[str] | None = None,
) -> Iterator[MermaidTriple]:
    if set_of_triple_ids is None:
        set_of_triple_ids = []

    _hacks_for_buildables(d)

    node_deps_from = build_node_with_dependencies(d)

    good_deps = [
        (k, list_to_dict_hack(d[k]))
        for k in node_deps_from.dependencies
        if _is_good_dep(list_to_dict_hack(d[k]))
    ]
    for k, v in good_deps:
        node_deps_to = build_node_with_dependencies(v)
        triple = MermaidTriple(node_deps_from.node, k, node_deps_to.node)
        triple_id = "-".join([f"{getattr(triple,f.name)}" for f in fields(triple)])
        if triple_id not in set_of_triple_ids and node_deps_to.node is not None:
            yield triple
            set_of_triple_ids.append(triple_id)
            if isinstance(v, dict):
                yield from generate_mermaid_triples(v, set_of_triple_ids)


def list_to_dict_hack(l: Any) -> dict | Any:
    if isinstance(l, list):
        return {str(k): v for k, v in enumerate(l)}
    else:
        return l


def _is_good_dep(couldbedep: Any) -> bool:
    if not isinstance(couldbedep, dict):
        if couldbedep is not None:
            logger.warning(f"{couldbedep} is no dict -> gets ignored")
        return False
    if "_target_" not in couldbedep and not is_dict_of_dataclasses(couldbedep):
        return False

    blacklisted = (
        isinstance(couldbedep, dict)
        and couldbedep.get("_target_", "").split(".")[-1] in CLASSES_BLACKLIST
    )
    return not blacklisted


def build_node_with_dependencies(obj: Any) -> NodeDependencies:
    assert obj is not None
    if isinstance(obj, dict):
        node_deps = _node_dependencies_from_dict(obj)
    else:
        # uuid cause I don't want builtin object to be concentrated in single node
        node_deps = NodeDependencies(
            MermaidNode(f"{uuid.uuid1()}", type(obj).__name__, params=obj),
            dependencies=[],
        )
    return node_deps


def _node_dependencies_from_dict(
    obj: dict,
) -> NodeDependencies | None:
    def is_param(pp: Any) -> bool:
        return isinstance(pp, str | int | float)
        # if isinstance(x,dict):
        #     keys=set(x.keys())
        #     is_a_param= len(set(SPECIAL_KEYS).intersection(keys))==0
        # elif :

    d: dict[str, Any] = obj
    params = [
        k for k, v in d.items() if is_param(v) and k not in SPECIAL_KEYS
    ]  # TODO(tilo): coupled too closely via SPECIAL_KEYS to nested-dataclass-serialization!
    dependencies = [
        k for k, v in d.items() if k not in params and k not in SPECIAL_KEYS
    ]
    if "_target_" in obj.keys():
        node = MermaidNode(
            str(obj["_id_"]),
            # node_name=obj.get("name", None), # make DAG too complex! cause names are very very long and redundant
            full_module_name=obj["_target_"],
            params={
                k: d[k] for k in params
            },  # {"name": obj["name"]} if "name" in obj else {},
        )
    elif is_dict_of_dataclasses(obj):
        node = MermaidNode(
            str(id(obj)),
            full_module_name=f"{Dict.__module__}.{Dict.__name__}",
            # params={
            #     k: d[k] for k in params
            # },  # {"name": obj["name"]} if "name" in obj else {},
        )
    else:
        raise NotImplementedError

    return NodeDependencies(node, dependencies)


def is_dict_of_dataclasses(d: dict) -> bool:
    return "_target_" not in d.keys() and any(
        isinstance(v, dict) and "_target_" in v.keys() for v in d.values()
    )


def _hacks_for_buildables(d: dict) -> None:
    def _maybe_dictify_list(d: dict) -> None:
        list_to_be_dictified = isinstance(d["data"], list)
        if list_to_be_dictified:
            d["data"] = {f"{i}": e for i, e in enumerate(d["data"])} | {
                "_target_": "list",
                "_id_": f"{uuid.uuid4()}",
            }

    hack_for_BuildableContainer = d.get("_target_", "").endswith("BuildableContainer")
    if hack_for_BuildableContainer:
        _maybe_dictify_list(d)
    hack_for_buildable_list = d.get("_target_", "").endswith("BuildableList")
    if hack_for_buildable_list:
        _maybe_dictify_list(d)
