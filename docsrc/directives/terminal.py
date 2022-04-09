import ast
import os
import re
import runpy
import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Any, Sequence, Optional, Type

import pexpect
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
    commands: Sequence[str],
    setup_command: Optional[str] = None,
    input: Optional[List[str]] = None,
) -> List[Command]:
    input = input or []
    orig_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        if setup_command:
            # Don't save the output of the setup command
            _run(setup_command)
        out_commands: List[Command] = []
        for i, command in enumerate(commands):
            try:
                this_command_input = input[i]
            except IndexError:
                this_command_input = None
            out_commands.append(_run(command, this_command_input))
        os.chdir(orig_dir)
    return out_commands


ansi_escape = re.compile(
    r"""
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
""",
    re.VERBOSE,
)


def _remove_bash_formatting_from_output(output: str) -> str:
    return ansi_escape.sub("", output)


def _get_terminal_output_with_prompt_at_end(output: str) -> str:
    formatted = _remove_bash_formatting_from_output(output)
    lines = formatted.split("\n")
    return "\n".join([*lines[:-1], "# " + lines[-1] + "$ "])


def _run(command: str, input: Optional[str] = None) -> Command:
    use_input = input.split("\n") if input else None
    stop_for_input_chars = ["]: ", r"0m: "]

    if use_input:
        process = pexpect.spawn(f'bash -c "{command}"', encoding="utf-8")
        all_stdout = ""
        for inp in use_input:
            process.expect_exact(stop_for_input_chars, timeout=10)
            this_stdout = process.before + process.after
            all_stdout += _get_terminal_output_with_prompt_at_end(this_stdout)
            process.sendline(inp)
        process.expect(pexpect.EOF)
        all_stdout += _remove_bash_formatting_from_output(process.before)
        return Command(input=command, output=all_stdout)

    output = subprocess.run(command, shell=True, capture_output=True, input=use_input)
    return Command(
        input=command, output=output.stdout.decode() + "\n" + output.stderr.decode()
    )


def _commands_to_list(commands: Sequence[Command]) -> List[str]:
    output: List[str] = []
    for command in commands:
        output.append(f"$ {command.input}")
        output.append(command.output)
    return output


def _get_list(input: str) -> List[str]:
    if not input.startswith("["):
        if input:
            return [input]
        return []
    return ast.literal_eval(input)


class RunTerminalDirective(SphinxDirective):
    required_arguments = 0
    option_spec = {"setup": directives.unchanged, "input": _get_list}
    has_content = True
    always_setup_commands: List[str] = []

    def run(self) -> List[Node]:
        setup_command: str = self.options.get("setup", "")
        if setup_command:
            use_commands = self.always_setup_commands + [setup_command]
        else:
            use_commands = self.always_setup_commands
        full_setup_command: str = " && ".join(use_commands)
        input: List[str] = self.options.get("input", [])
        output = _run_commands_in_temp_dir(
            self.content, full_setup_command, input=input
        )
        text = _commands_to_list(output)
        return [termy_block(self.env.myst_config, text)]


def create_run_terminal_directive_with_setup(
    setup_commands: Sequence[str],
) -> Type[SphinxDirective]:
    class RunTerminalDirectiveWithSetup(RunTerminalDirective):
        always_setup_commands = list(setup_commands)

    return RunTerminalDirectiveWithSetup
