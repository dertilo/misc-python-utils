import logging

from misc_python_utils.beartypes import Dataclass
from misc_python_utils.mermaid_utils.mermaid_data_models import MermaidNode
from misc_python_utils.mermaid_utils.mermaid_markdown_diagrams import mermaid_flowchart

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html

HTML = str


def mermaid_html_dag(
    dag: Dataclass,
    display_params: bool = False,
    print_it: bool = False,
) -> HTML:
    logger.info(f"creatign mermaid dag html for {dag.__class__.__name__}")
    MermaidNode.display_params = display_params
    text = mermaid_flowchart(dag, is_dependencies=False)
    if print_it:
        print(text)  # noqa: T201
    name = f"<h1>{dag.name}</h1>" if hasattr(dag, "name") else ""
    return f"""{name}
<div class="mermaid">
{text}
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
