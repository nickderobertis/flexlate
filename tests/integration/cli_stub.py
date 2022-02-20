import shlex
from pathlib import Path
from typing import Union, Sequence, Optional, List

from click.testing import Result

from flexlate.add_mode import AddMode
from flexlate.cli import cli
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.main import Flexlate
from flexlate.template_data import TemplateData
from typer.testing import CliRunner

from tests import ext_click

runner = CliRunner()


class CLIRunnerException(Exception):
    pass


def fxt(
    args: Union[str, Sequence[str]],
    input_data: Optional[Union[TemplateData, List[TemplateData]]] = None,
) -> Result:
    text_input = _get_text_input(input_data)
    result = runner.invoke(cli, args, input=text_input)
    if result.exit_code != 0:
        output = ext_click.result_to_message(result)
        command = shlex.join(["fxt", *args])
        raise CLIRunnerException(
            f"{command} with input {text_input} exited with code {result.exit_code}.\n{output}"
        )
    return result


def _get_text_input(
    input_data: Optional[Union[TemplateData, List[TemplateData]]]
) -> Optional[str]:
    if input_data is None:
        return None
    if isinstance(input_data, list):
        return "\n".join(_template_data_to_text_input(data) for data in input_data)
    return _template_data_to_text_input(input_data)


def _template_data_to_text_input(input_data: TemplateData) -> str:
    return "\n".join(str(value) for value in input_data.values())


class CLIStubFlexlate(Flexlate):
    def init_project(
        self,
        path: Path = Path("."),
        default_add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        template_path_from: Optional[str] = None,
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
                *_flag_if_not_none(template_path_from, "from"),
            ]
        )

    def init_project_from(
        self,
        template_path: str,
        path: Path = Path("."),
        template_version: Optional[str] = None,
        data: Optional[TemplateData] = None,
        default_folder_name: str = "project",
        no_input: bool = False,
        quiet: bool = False,
        default_add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    ):
        # Answer about the generated folder if prompted
        project_folder_answer = {"folder": default_folder_name}
        all_data = {**(data or {}), **project_folder_answer}

        fxt(
            [
                "init-from",
                template_path,
                str(path),
                *_flag_if_not_none(template_version, "version"),
                "--folder-name",
                default_folder_name,
                *_bool_flag(no_input, "no-input"),
                *_bool_flag(quiet, "quiet"),
                "--add-mode",
                default_add_mode.value,
                "--merged-branch-name",
                merged_branch_name,
                "--template-branch-name",
                template_branch_name,
            ],
            input_data=all_data,
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
        quiet: bool = False,
    ):
        fxt(
            [
                "remove",
                "source",
                template_name,
                "--root",
                str(template_root),
                *_bool_flag(quiet, "quiet"),
            ]
        )

    def apply_template_and_add(
        self,
        name: str,
        data: Optional[TemplateData] = None,
        out_root: Path = Path("."),
        add_mode: Optional[AddMode] = None,
        no_input: bool = False,
        quiet: bool = False,
    ):
        fxt(
            [
                "add",
                "output",
                name,
                str(out_root),
                *_bool_flag(no_input, "no-input"),
                *_bool_flag(quiet, "quiet"),
                *_flag_if_not_none(
                    add_mode.value if add_mode is not None else None, "add-mode"
                ),
            ],
            input_data=data,
        )

    def remove_applied_template_and_output(
        self, template_name: str, out_root: Path = Path("."), quiet: bool = False
    ):
        fxt(
            [
                "remove",
                "output",
                template_name,
                str(out_root),
                *_bool_flag(quiet, "quiet"),
            ]
        )

    def update(
        self,
        names: Optional[List[str]] = None,
        data: Optional[Sequence[TemplateData]] = None,
        no_input: bool = False,
        quiet: bool = False,
        project_path: Path = Path("."),
    ):
        fxt(
            [
                "update",
                *_value_if_not_none(names),
                "--path",
                str(project_path),
                *_bool_flag(no_input, "no-input"),
                *_bool_flag(quiet, "quiet"),
            ],
            input_data=data,
        )

    def undo(self, num_operations: int = 1, project_path: Path = Path(".")):
        return fxt(["undo", str(num_operations), "--path", str(project_path)])

    def sync(
        self,
        no_input: bool = False,
        quiet: bool = False,
        project_path: Path = Path("."),
    ):
        return fxt(
            [
                "sync",
                str(project_path),
                *_bool_flag(no_input, "no-input"),
                *_bool_flag(quiet, "quiet"),
            ]
        )

    def merge_flexlate_branches(
        self,
        branch_name: Optional[str] = None,
        delete: bool = True,
        project_path: Path = Path("."),
    ):
        return fxt(
            [
                "merge",
                *_value_if_not_none(branch_name),
                *_bool_flag(not delete, "no-delete"),
                "--path",
                str(project_path),
            ]
        )

    def push_main_flexlate_branches(
        self,
        remote: str = "origin",
        project_path: Path = Path("."),
    ):
        return fxt(["push", "main", "--remote", remote, "--path", str(project_path)])

    def push_feature_flexlate_branches(
        self,
        feature_branch: Optional[str] = None,
        remote: str = "origin",
        project_path: Path = Path("."),
    ):
        return fxt(
            [
                "push",
                "feature",
                *_value_if_not_none(feature_branch),
                "--remote",
                remote,
                "--path",
                str(project_path),
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
