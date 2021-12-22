from pathlib import Path
from typing import Union, Sequence, Optional, List

from click.testing import Result

from flexlate.add_mode import AddMode
from flexlate.cli import cli
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.main import Flexlate
from flexlate.template_data import TemplateData
from typer.testing import CliRunner

runner = CliRunner()


def fxt(
    args: Union[str, Sequence[str]], input_data: Optional[TemplateData] = None
) -> Result:
    text_input = "\n".join(input_data.values()) if input_data is not None else None
    print(f"Running {args} with input {text_input}")
    return runner.invoke(cli, args, input=text_input)


class CLIStubFlexlate(Flexlate):
    def init_project(
        self,
        path: Path = Path("."),
        default_add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        user: bool = False,
    ):
        fxt(
            [
                "init",
                str(path),
                "--add-mode",
                default_add_mode.value,
                "--merged-branch-name",
                merged_branch_name,
                "--template-branch-name",
                template_branch_name,
                *_bool_flag(user, "user"),
            ]
        )

    def add_template_source(
        self,
        path: str,
        name: Optional[str] = None,
        target_version: Optional[str] = None,
        template_root: Path = Path("."),
        add_mode: Optional[AddMode] = None,
    ):
        fxt(
            [
                "add",
                "source",
                path,
                *_value_if_not_none(name),
                *_flag_if_not_none(target_version, "version"),
                "--root",
                str(template_root),
                *_flag_if_not_none(
                    add_mode.value if add_mode is not None else None, "add-mode"
                ),
            ]
        )

    def remove_template_source(
        self,
        template_name: str,
        template_root: Path = Path("."),
    ):
        fxt(["remove", "source", template_name, "--root", str(template_root)])

    def apply_template_and_add(
        self,
        name: str,
        data: Optional[TemplateData] = None,
        out_root: Path = Path("."),
        add_mode: Optional[AddMode] = None,
        no_input: bool = False,
    ):
        fxt(
            [
                "add",
                "output",
                name,
                "--root",
                str(out_root),
                *_bool_flag(no_input, "no-input"),
                *_flag_if_not_none(
                    add_mode.value if add_mode is not None else None, "add-mode"
                ),
            ],
            input_data=data,
        )

    def update(
        self,
        names: Optional[List[str]] = None,
        no_input: bool = False,
        project_path: Path = Path("."),
    ):
        fxt(
            [
                "update",
                *_value_if_not_none(names),
                "--path",
                str(project_path),
                *_bool_flag(no_input, "no-input"),
            ]
        )


def _bool_flag(value: bool, name: str) -> List[str]:
    return [f"--{name}"] if value else []


def _flag_if_not_none(value: Optional[str], name: str) -> List[str]:
    return [f"--{name}", value] if value else []


def _value_if_not_none(value: Union[str, List[str], None]) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return value
