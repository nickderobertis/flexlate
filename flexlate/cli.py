from pathlib import Path
from typing import Optional, List

import typer

from flexlate.add_mode import AddMode
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.main import Flexlate

cli = typer.Typer()
app = Flexlate()

add_cli = typer.Typer(
    help="Add template sources and generate new projects and "
    "files from existing template sources"
)

TEMPLATE_ROOT_DOC = (
    "The root directory to render the template from, defaults to current"
)
ADD_MODE_DOC = (
    "Local adds the config to the template root, project adds it to the project "
    "config (which may also be template root), and user adds it to the user config"
)
NO_INPUT_DOC = "Whether to proceed without any input from the user (useful for automation, e.g. CI systems)"
PROJECT_PATH_DOC = "The location of the project"


TEMPLATE_ROOT_OPTION = typer.Option(
    Path("."),
    "--root",
    "-r",
    help=TEMPLATE_ROOT_DOC,
    show_default=False,
)
ADD_MODE_OPTION = typer.Option(
    None,
    "--add-mode",
    "-a",
    help=ADD_MODE_DOC,
    case_sensitive=False,
    show_choices=True,
)
NO_INPUT_OPTION = typer.Option(False, "--no-input", "-n", show_default=False)


@add_cli.command(name="source")
def add_source(
    path: str = typer.Argument(
        ..., help="Template source. Can be a file path or a git url"
    ),
    name: Optional[str] = typer.Argument(
        None,
        help="A custom name for the template. By default, it will use the folder or repo name",
    ),
    version: Optional[str] = typer.Option(
        None,
        "--version",
        "-v",
        help="A specific version to target. Only useful for git repos, pass a branch name or commit SHA",
        show_default=False,
    ),
    template_root: Path = TEMPLATE_ROOT_OPTION,
    add_mode: Optional[AddMode] = ADD_MODE_OPTION,
):
    """
    Adds a new template source, so that files can be generated from it
    """
    app.add_template_source(
        path,
        name=name,
        target_version=version,
        template_root=template_root,
        add_mode=add_mode,
    )


@add_cli.command(name="output")
def generate_applied_template(
    name: str = typer.Argument(
        ...,
        help="The name of the template. It must match a name in template sources",
    ),
    template_root: Path = TEMPLATE_ROOT_OPTION,
    add_mode: Optional[AddMode] = ADD_MODE_OPTION,
    no_input: bool = NO_INPUT_OPTION,
):
    """
    Applies a template to a given location, and stores it in config so it can be updated
    """
    app.apply_template_and_add(
        name, out_root=template_root, add_mode=add_mode, no_input=no_input
    )


cli.add_typer(add_cli, name="add")


@cli.command(name="init")
def init_project(
    path: Path = typer.Argument(Path("."), help=PROJECT_PATH_DOC),
    default_add_mode: AddMode = typer.Option(
        AddMode.LOCAL,
        "--add-mode",
        "-a",
        help=ADD_MODE_DOC,
        case_sensitive=False,
        show_choices=True,
    ),
    merged_branch_name: str = typer.Option(
        DEFAULT_MERGED_BRANCH_NAME,
        help="The name of the branch that flexlate creates to store the merges between template updates and the project",
    ),
    template_branch_name: str = typer.Option(
        DEFAULT_TEMPLATE_BRANCH_NAME,
        help="The name of the branch that flexlate creates that stores only the template output",
    ),
    user: bool = typer.Option(
        False,
        "--user",
        help="Store the flexlate project configuration in the user directory rather than in the project",
    ),
):
    """
    Initializes a flexlate project. This must be run before other commands
    """
    app.init_project(
        path,
        default_add_mode=default_add_mode,
        merged_branch_name=merged_branch_name,
        template_branch_name=template_branch_name,
        user=user,
    )


@cli.command(name="update")
def update_templates(
    names: Optional[List[str]] = typer.Argument(
        None,
        help="Optional names of templates to updates. Defaults to all templates",
        show_default=False,
    ),
    no_input: bool = NO_INPUT_OPTION,
    path: Path = typer.Option(Path("."), help=PROJECT_PATH_DOC),
):
    """
    Updates applied templates in the project to the newest versions
    available that still satisfy source target versions
    """
    app.update(names=names, no_input=no_input, project_path=path)


if __name__ == "__main__":
    cli()
