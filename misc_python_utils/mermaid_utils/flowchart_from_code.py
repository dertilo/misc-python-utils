# flake8: noqa
import inspect
import logging
import subprocess
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from pyflowchart import Flowchart

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html

NODE_TYPES = [
    "start: start",
    "end: end",
    "condition:",
    "operation:",
    "inputoutput: input:",
    "inputoutput: output:",
]


def split_condition(from_node) -> tuple[str, str]:  # noqa: ANN001
    from_node, cond = from_node.split("(")
    assert cond.endswith(")")
    cond = cond.replace(")", "")
    return from_node, f"| {cond} |"


def mermaid_html(name: str, mermaid_markdown: str) -> str:
    return f"""{name}
<div class="mermaid">
{mermaid_markdown}
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>mermaid.initialize(
    {{
    startOnLoad:true,
    theme: 'forest',
    securityLevel: 'loose',
    maxTextSize: 90000
    }}
    );</script>

"""


from black import FileMode, InvalidInput, format_str  # noqa: E402

square = lambda s: f'{s[0]}["{s[1]}"]'
stadium = lambda s: f'{s[0]}(["{s[1]}"]):::style4'
# diamond = lambda s: f"{{\"{s}\"}}" # grows too big for long text
hexagon = lambda s: f'{s[0]}{{{{"{s[1]}"}}}}:::style0'
left_parallelogram = lambda s: f'{s[0]}[\\"{s[1]}"\\]:::style1'
NODE_FORMATTERS = {
    "start: start": stadium,
    "end: end": stadium,
    "condition:": hexagon,
    "operation:": square,
    "inputoutput: input:": left_parallelogram,
    "inputoutput: output:": left_parallelogram,
}
# palette: https://www.color-hex.com/color-palette/5361

palette = """
	#ffb3ba 	(255,179,186)
	#ffdfba 	(255,223,186)
	#ffffba 	(255,255,186)
	#baffc9 	(186,255,201)
	#bae1ff 	(186,225,255)
"""

import ast  # noqa: E402


@dataclass(slots=True)
class Import:
    module: list[str]
    name: str
    alias: str


def get_imports(path: str) -> Iterator[Import]:
    """
    copypasted from: https://stackoverflow.com/questions/9008451/python-easy-way-to-read-all-import-statements-from-py-module
    """
    with open(path) as fh:  # noqa: PTH123
        root = ast.parse(fh.read(), path)

    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.Import):
            module = []
        elif isinstance(node, ast.ImportFrom):
            module = node.module.split(".")
        else:
            continue

        for n in node.names:
            yield Import(module, n.name, n.asname)


@dataclass(slots=True)
class TripleBuilder:
    id2name: dict[str, str]

    def get_name(self, k: str) -> str:
        if k in self.id2name:
            type_name = self.id2name.pop(k)
            for op in NODE_TYPES:
                if type_name.startswith(op):
                    name = type_name[len(op) :]
                    try:  # noqa: SIM105
                        name = format_str(name, mode=FileMode())
                    except InvalidInput:
                        pass
                    name = name.replace('"', "'")

                    self.id2name[k] = op
                    break
            else:
                logger.warning(f"unknown: {type_name}")
                op, name = None, type_name
            return f"{NODE_FORMATTERS.get(op,square)((k,name))}" if len(name) > 0 else k
        else:
            return k

    def build_triples(
        self,
        raw_triples: Iterable[tuple[str, str, str]],
    ) -> Iterator[tuple[str, str, str]]:
        yield from ((self.get_name(a), e, self.get_name(b)) for a, e, b in raw_triples)


def get_python_file_from_function_name(function_name: str, current_file: str) -> str:
    """

    :param function_name: name of the function to find the python file for
    :return: python-file containing the function
    """
    all_imports = get_imports(current_file)
    for imp in all_imports:
        if imp.name == function_name:
            # import function from module
            import importlib

            module = importlib.import_module(".".join(imp.module))
            function_handle = module["function_name"]
            # get python-file function-handle
            return inspect.getfile(function_handle)

    raise ValueError(f"could not find {function_name=}")  # noqa: EM102, TRY003


def mermaid_flow_from_python_code(code: str, field: str) -> str:
    fc = Flowchart.from_code(code, field=field, inner=True, simplify=False)
    flow = fc.flowchart()
    print(flow)  # noqa: T201
    nodes, graph = flow.split("\n\n")
    id2name = [line.split("=>") for line in nodes.split("\n") if len(line) > 0]
    id2name = {k: v for k, v in id2name}  # noqa: C416
    builder = TripleBuilder(id2name)

    from_to = [line.split("->") for line in graph.split("\n") if len(line) > 0]
    triples = [
        (*split_condition(ft[0]), ft[1]) if "(" in ft[0] else (ft[0], "", ft[1])
        for ft in from_to
    ]
    triples = builder.build_triples(triples)
    edges = "\n".join(
        [f"{a} --> {edge} {b}" for a, edge, b in triples],
    )
    colors = [line.split("\t") for line in palette.split("\n") if len(line) > 0]
    style_classes = [
        f"classDef style{k!s} fill:{hexcolor}"
        for k, (_, hexcolor, _) in enumerate(colors)
    ]
    style_classes_s = "\n".join(style_classes)
    mermaid_flow = f"""flowchart TD
{style_classes_s}
{edges}

"""
    return mermaid_flow  # noqa: RET504


def local_workflow_detailed(your_code: str, your_patience=999) -> None:
    code_changes = cmdline_run("poetry run fixcode")
    git_commit(code_changes)
    stdout, exit_code = cmdline_run("poetry run pythonlinter")
    while exit_code != 0:
        if stdout != "passed ruff linter! ✨ 🍰 ✨":
            noqa_comments = cmdline_run("poetry run addnoqa")
            refactor(noqa_comments)
        elif stdout != "passed flake8 linter! ✨ 🍰 ✨":
            refactor(your_code)
        else:
            git_commit(your_code)
            break  # you are done!
        code_changes = cmdline_run(
            "poetry run fixcode"
        )  # cause "YOU-refactor" might messup code-format or introduce new "violations"
        git_commit(code_changes)
        stdout = cmdline_run("poetry run pythonlinter")

    git_push(your_code)


def local_workflow(your_code: str, your_patience=999) -> None:
    git_commit(cmdline_run("poetry run fixcode"))
    stdout, exit_code = cmdline_run("poetry run pythonlinter")
    while exit_code != 0:
        if stdout != "passed ruff linter! ✨ 🍰 ✨":
            noqa_comments = cmdline_run("poetry run addnoqa")
            refactor(noqa_comments)
        elif stdout != "passed flake8 linter! ✨ 🍰 ✨":
            refactor(your_code)
        else:
            git_commit(your_code)
            break  # you are done!
        git_commit(cmdline_run("poetry run fixcode"))
        stdout = cmdline_run("poetry run pythonlinter")

    git_push(your_code)


def git_commit(changes) -> None:
    pass


def git_push(changes) -> None:
    pass


def refactor(code) -> None:
    pass


def cmdline_run(cmd) -> str:
    stdout = subprocess.check_output(cmd, shell=True, text=True)
    return stdout


if __name__ == "__main__":
    from misc_python_utils.file_utils.readwrite_files import write_file

    with open(  # noqa: PTH123
        __file__,
    ) as f:
        code = f.read()

    mermaid_flow = mermaid_flow_from_python_code(
        code,
        field="local_workflow_detailed",
    )
    print(mermaid_flow)  # noqa: T201
    write_file("mermaid.html", mermaid_html("flowchart", mermaid_flow))
