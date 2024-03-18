from nested_dataclass_serialization.dataclass_serialization import encode_dataclass

from misc_python_utils.beartypes import Dataclass
from misc_python_utils.file_utils.readwrite_files import write_file
from misc_python_utils.mermaid_utils._mermaid_markdown_from_nested_dataclasses import (
    generate_mermaid_triples,
)


def write_dataclass_to_mermaid(
    file: str,
    o: Dataclass,
    additional_skipkeys: list[str] | None = None,
) -> None:
    flow_chart = mermaid_flowchart(o, additional_skipkeys)
    write_file(file, f"```mermaid\n\n{flow_chart}```")


def mermaid_flowchart(
    o: Dataclass,
    additional_skipkeys: list[str] | None = None,
    is_dependencies: bool = True,
) -> str:
    skip_keys = ["cache_dir", "cache_base"]
    if additional_skipkeys is not None:
        skip_keys += additional_skipkeys

    d = encode_dataclass(o, skip_keys=skip_keys)
    return dict_to_mermaid(d, is_dependencies)


def dict_to_mermaid(d: dict, is_dependencies: bool = True) -> str:
    dependencies_builder = (
        lambda triple: f"{triple.node_from} --> | {triple.edge_name} | {triple.node_to}"
    )
    flow_builder = (
        lambda triple: f"{triple.node_to} --> | {triple.edge_name} | {triple.node_from}"
    )
    edges = "\n".join(
        [
            dependencies_builder(triple) if is_dependencies else flow_builder(triple)
            for triple in generate_mermaid_triples(d)
        ],
    )
    return f"flowchart TD\n\n{edges}\n"


# def process_node_name(n: str) -> str:
#     return n.replace("__main__.", "")
