import ast
import os
import re
import runpy
import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Any, Sequence, Optional, Type, Tuple

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
    cwd: Path


def _run_commands_in_temp_dir(
    commands: Sequence[str],
    setup_command: Optional[str] = None,
    input: Optional[List[str]] = None,
    allow_exceptions: bool = False,
) -> List[Command]:
    def run(command: str, last_cwd: Path, input: Optional[str] = None) -> Command:
        try:
            return _run(command, last_cwd, input)
        except (
            pexpect.exceptions.EOF,
            pexpect.exceptions.TIMEOUT,
            CommandException,
        ) as e:
            if isinstance(e, CommandException):
                if allow_exceptions:
                    return Command(
                        input=command,
                        output=e.output,
                        cwd=e.cwd,
                    )
                raise CommandException(
                    f"Command failed: {command} due to {e} as "
                    f"part of running {commands=} {setup_command=} {input=}",
                    output=e.output,
                    cwd=e.cwd,
                ) from e
            exc_parts = e.value.split("\n")
            output = [
                part
                for part in exc_parts
                if part.startswith("before (last 100 chars): ")
            ][0]
            output_without_prefix = output[len("before (last 100 chars): ") :]
            raise CommandException(
                f"Command failed: {command} as "
                f"part of running {commands=} {setup_command=} {input=}",
                output_without_prefix,
                last_cwd,
            ) from e

    input = input or []
    orig_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        last_cwd = Path(tmpdir)
        if setup_command:
            # Don't save the output of the setup command
            out_command = run(setup_command, last_cwd)
            last_cwd = out_command.cwd
        out_commands: List[Command] = []
        for i, command in enumerate(commands):
            try:
                this_command_input = input[i]
            except IndexError:
                this_command_input = None
            out_command = run(command, last_cwd, input=this_command_input)
            last_cwd = out_command.cwd
            out_commands.append(out_command)
        os.chdir(orig_dir)
    return out_commands


class CommandException(Exception):
    def __init__(self, message: str, output: str, cwd: Path) -> None:
        self.output = output
        self.cwd = cwd
        super().__init__(message)

    def __str__(self) -> str:
        return f"{super().__str__()}\n{self.cwd=} with output:\n{self.output}"


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


def _remove_overwritten_output(output: str) -> str:
    lines = output.split("\r\n")
    clean_lines: List[str] = []
    for line in lines:
        within_lines = line.split("\r")
        if len(within_lines) == 1:
            clean_lines.append(line)
        else:
            # The terminal is trying to overwrite the existing output
            # We don't want to display this multiple times in the output, so
            # simply take the last one
            clean_lines.append(within_lines[-1])
    return "\r\n".join(clean_lines)


def _get_terminal_output_with_prompt_at_end(output: str) -> str:
    formatted = _remove_overwritten_output(_remove_bash_formatting_from_output(output))
    lines = formatted.split("\r\n")

    return "\r\n".join([*lines[:-1], "# " + lines[-1] + "$ "])


def _get_real_output_and_cwd_from_output(
    output: str, last_cwd: Path
) -> Tuple[str, Path]:
    lines = output.split("\r\n")
    # Find index of last real line
    i = 0
    for i, line in enumerate(reversed(lines)):
        if line:
            break
    last_real_idx = -(i + 1)
    real_output = "\r\n".join(lines[:last_real_idx])
    cwd = Path(lines[last_real_idx].strip())
    if not cwd.exists():
        raise CommandException(f"{cwd=} does not exist.", output, last_cwd)
    return real_output, cwd


def _run(command: str, cwd: Path, input: Optional[str] = None) -> Command:
    use_input = input.split("\n") if input else []
    stop_for_input_chars = ["]: ", r"0m: "]

    process = pexpect.spawn(
        f"bash -c \"cd '{cwd}' && {command} && printf '\\n' && pwd\"", encoding="utf-8"
    )
    all_stdout = ""
    for inp in use_input:
        process.expect_exact(stop_for_input_chars, timeout=10)
        this_stdout = process.before + process.after
        all_stdout += _get_terminal_output_with_prompt_at_end(this_stdout)
        process.sendline(inp)
    process.expect(pexpect.EOF)
    unformatted = _remove_bash_formatting_from_output(process.before)
    real_output, new_cwd = _get_real_output_and_cwd_from_output(unformatted, cwd)
    all_stdout += real_output
    return Command(input=command, output=all_stdout, cwd=new_cwd)


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
    option_spec = {
        "setup": directives.unchanged,
        "input": _get_list,
        "allow-exceptions": directives.flag,
    }
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
        allow_exceptions: bool = "allow-exceptions" in self.options
        output = _run_commands_in_temp_dir(
            self.content,
            full_setup_command,
            input=input,
            allow_exceptions=allow_exceptions,
        )
        text = _commands_to_list(output)
        return [termy_block(self.env.myst_config, text)]


def create_run_terminal_directive_with_setup(
    setup_commands: Sequence[str],
) -> Type[SphinxDirective]:
    class RunTerminalDirectiveWithSetup(RunTerminalDirective):
        always_setup_commands = list(setup_commands)

    return RunTerminalDirectiveWithSetup
