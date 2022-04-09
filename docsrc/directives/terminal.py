import os
import runpy
import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Any, Sequence, Optional

from docutils.nodes import Node
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from myst_parser import create_myst_config
from myst_parser.docutils_renderer import DocutilsRenderer
from myst_parser.main import create_md_parser, MdParserConfig
from pydantic import BaseModel
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
    node.update_basic_atts({"classes": ["highlight"]})
    out_node.append(node)
    return out_node


class AnimatedTerminalDirective(SphinxDirective):
    required_arguments = 0
    has_content = True

    def run(self) -> List[Node]:
        return [termy_block(self.env.myst_config, self.content)]


class Command(BaseModel):
    input: str
    output: str


def _run_commands_in_temp_dir(
    commands: Sequence[str], setup_command: Optional[str] = None
) -> List[Command]:
    orig_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        if setup_command:
            # Don't save the output of the setup command
            _run(setup_command)
        out_commands: List[Command] = [_run(command) for command in commands]
        os.chdir(orig_dir)
    return out_commands


def _run(command: str) -> Command:
    output = subprocess.run(command, shell=True, capture_output=True)
    return Command(
        input=command, output=output.stdout.decode() + "\n" + output.stderr.decode()
    )


def _commands_to_list(commands: Sequence[Command]) -> List[str]:
    output: List[str] = []
    for command in commands:
        output.append(f"$ {command.input}")
        output.append(command.output)
    return output


class RunTerminalDirective(SphinxDirective):
    required_arguments = 0
    option_spec = {"setup": directives.unchanged}
    has_content = True

    def run(self) -> List[Node]:
        setup_command: str = self.options.get("setup", "")
        output = _run_commands_in_temp_dir(self.content, setup_command)
        text = _commands_to_list(output)
        return [termy_block(self.env.myst_config, text)]
