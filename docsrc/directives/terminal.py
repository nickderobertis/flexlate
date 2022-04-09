import os
import runpy
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Any

from docutils.nodes import Node
from docutils.statemachine import StringList
from myst_parser import create_myst_config
from myst_parser.docutils_renderer import DocutilsRenderer
from myst_parser.main import create_md_parser, MdParserConfig
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from docutils import nodes


def termy_block(config: MdParserConfig, src: StringList) -> nodes.container:
    parser = create_md_parser(config, DocutilsRenderer)
    out_node = nodes.container()
    out_node.update_basic_atts({"classes": ["termy"]})
    parser.renderer.setup_render(dict(myst_config=config), {})
    text = "\n".join(src)
    node = parser.renderer.create_highlighted_code_block(text, "console")
    out_node.append(node)
    return out_node




class AnimatedTerminalDirective(SphinxDirective):
    required_arguments = 0
    has_content = True

    def run(self) -> List[Node]:
        return [
            termy_block(self.env.myst_config, self.content)
        ]
