import importlib
import json
import logging
from dataclasses import dataclass
from typing import Any, ClassVar

from result import Err, Ok

from misc_python_utils.error_handling.as_result_logged import (
    as_result_logged_panic_for_param_violations,
)
from misc_python_utils.gitrepo_utils.git_repo_state import (
    UncommittedChanges,
    permanent_link_from_class,
)

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html

UNCOMMITTED_CHANGES = set()


@dataclass
class MermaidNode:
    id_: str
    full_module_name: str
    node_name: str | None = None
    params: Any | None = None
    display_params: ClassVar[bool] = True
    raw_name: ClassVar[bool] = False

    def __post_init__(self):
        if "." not in self.full_module_name:
            self.full_module_name = f"builtin.{self.full_module_name}"

    @property
    def class_name(self) -> str:
        return (
            self.full_module_name
            if self.raw_name
            else self.full_module_name.split(".")[-1]
        )

    def __repr__(self) -> str:
        text = self.class_name
        params = self.params
        if params is not None and self.display_params:
            text = self._add_params(params, text)
        elif self.node_name is not None:
            text = f"{self.class_name}\n{self.node_name}"
        global UNCOMMITTED_CHANGES  # noqa: PLW0602
        clazz = self._import_class()
        if clazz.is_ok() and clazz.ok() is not None:
            match permanent_link_from_class(clazz.ok()):
                case Ok(link):
                    text = f'<a href="{link}">{text}</a>'
                case Err(UncommittedChanges(msg)):
                    if msg not in UNCOMMITTED_CHANGES:
                        UNCOMMITTED_CHANGES.add(msg)
                        logger.warning(f"uncommitted changes in {msg}")
                case Err(ImportError()):
                    pass
                case Err("did not find git repo"):
                    pass  # if class comes from "normal" python dependency installed in some env it is expected to not be inside a gitrepo
                case Err(some_error):
                    logger.error(f"{some_error}")

        return f'{self.id_}["{text}"]'

    @as_result_logged_panic_for_param_violations(ImportError)
    def _import_class(self) -> type | None:
        module_name = ".".join(self.full_module_name.split(".")[:-1])
        if module_name == "builtin":
            clazz = None
        else:
            clazz = getattr(
                importlib.import_module(
                    module_name,
                ),
                self.class_name,
            )
        return clazz  # noqa: RET504

    def _add_params(self, params: dict, text: str) -> str:
        params_kv = (
            json.dumps(params, indent=4)
            .replace("{", "")
            .replace("}", "")
            .replace('"', "'")
            .replace(":", "=")
        )
        return f"{text}({params_kv})"


@dataclass(slots=True, frozen=True)
class NodeDependencies:
    node: MermaidNode | None
    dependencies: list[str]


@dataclass(slots=True, frozen=True)
class MermaidTriple:
    node_from: MermaidNode
    edge_name: str
    node_to: MermaidNode


@dataclass
class Dict(dict):
    pass
