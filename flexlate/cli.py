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
    "The root directory the template should be rendered from, defaults to current"
)
ADD_MODE_DOC = (
    "Local adds the config to the template root, project adds it to the project "
    "config (which may also be template root), and user adds it to the user config"
)
NO_INPUT_DOC = "Whether to proceed without any input from the user (useful for automation, e.g. CI systems)"
PROJECT_PATH_DOC = "The location of the project"
MERGED_BRANCH_DOC = "The name of the branch that flexlate creates to store the merges between template updates and the project"
TEMPLATE_BRANCH_DOC = (
    "The name of the branch that flexlate creates that stores only the template output"
)
PROJECT_USER_DOC = "Store the flexlate project configuration in the user directory rather than in the project"
TARGET_VERSION_DOC = "A specific version to target. Only useful for git repos, pass a branch name or commit SHA"
TEMPLATE_SOURCE_EXTRA_DOC = "Can be a file path or a git url"

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
VERSION_OPTION = typer.Option(
    None,
    "--version",
    "-v",
    help=TARGET_VERSION_DOC,
    show_default=False,
)


@add_cli.command(name="source")
def add_source(
    path: str = typer.Argument(
        ..., help=f"Template source. {TEMPLATE_SOURCE_EXTRA_DOC}"
    ),
    name: Optional[str] = typer.Argument(
        None,
        help="A custom name for the template. By default, it will use the folder or repo name",
    ),
    version: Optional[str] = VERSION_OPTION,
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

remove_cli = typer.Typer(
    help="Remove template sources and previously generated outputs"
)


@remove_cli.command(name="source")
def remove_template_source(
    template_name: str = typer.Argument(
        ..., help="The name of the template source to remove"
    ),
    template_root: Path = TEMPLATE_ROOT_OPTION,
):
    app.remove_template_source(template_name, template_root=template_root)


@remove_cli.command(name="output")
def remove_template_output(
    template_name: str = typer.Argument(
        ...,
        help="The name of the template source corresponding to "
        "the applied template output to remove",
    ),
    template_root: Path = TEMPLATE_ROOT_OPTION,
):
    app.remove_applied_template_and_output(template_name, out_root=template_root)


cli.add_typer(remove_cli, name="remove")


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
        DEFAULT_MERGED_BRANCH_NAME, help=MERGED_BRANCH_DOC
    ),
    template_branch_name: str = typer.Option(
        DEFAULT_TEMPLATE_BRANCH_NAME,
        help=TEMPLATE_BRANCH_DOC,
    ),
    user: bool = typer.Option(
        False,
        "--user",
        help=PROJECT_USER_DOC,
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


@cli.command(name="init-from")
def init_project_from(
    template_path: str = typer.Argument(
        ...,
        help=f"A template source path to initialize the project from. {TEMPLATE_SOURCE_EXTRA_DOC}",
    ),
    path: Path = typer.Argument(Path("."), help=PROJECT_PATH_DOC),
    version: Optional[str] = VERSION_OPTION,
    folder_name: str = typer.Option(
        "project",
        "--folder-name",
        "-f",
        help="The name of the outputted folder. This only applies on templates that don't set the name of the folder (Copier)",
    ),
    no_input: bool = NO_INPUT_OPTION,
    default_add_mode: AddMode = typer.Option(
        AddMode.LOCAL,
        "--add-mode",
        "-a",
        help=ADD_MODE_DOC,
        case_sensitive=False,
        show_choices=True,
    ),
    merged_branch_name: str = typer.Option(
        DEFAULT_MERGED_BRANCH_NAME, help=MERGED_BRANCH_DOC
    ),
    template_branch_name: str = typer.Option(
        DEFAULT_TEMPLATE_BRANCH_NAME,
        help=TEMPLATE_BRANCH_DOC,
    ),
):
    """
    Generates a project from a template and sets it up as a Flexlate project.
    """
    app.init_project_from(
        template_path,
        path,
        template_version=version,
        default_folder_name=folder_name,
        no_input=no_input,
        default_add_mode=default_add_mode,
        merged_branch_name=merged_branch_name,
        template_branch_name=template_branch_name,
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


@cli.command(name="undo")
def undo(
    num_operations: int = typer.Argument(
        1,
        help="Number of flexlate operations to undo",
    ),
    path: Path = typer.Option(Path("."), help=PROJECT_PATH_DOC),
):
    """
    Undoes the last flexlate operation, like ctrl/cmd + z for flexlate.
    Note that this modifies the git history, discarding the last commits.
    It has protections against deleting user commits but you should only
    use this on a feature branch.
    :return:
    """
    app.undo(num_operations=num_operations, project_path=path)


@cli.command(name="sync")
def sync(
    path: Path = typer.Argument(Path("."), help=PROJECT_PATH_DOC),
    no_input: bool = NO_INPUT_OPTION,
):
    """
    Syncs manual changes to the flexlate branches, and updates templates
    accordingly. This is useful if you want to move or modify flexlate configs
    after they are created, but there is no command in the CLI for it.
    This is currently the way to update template versions until there is a
    specific command for it: manually change the version and run sync.

    Note: Be sure to commit your changes before running sync
    :return:
    """
    app.sync(no_input=no_input, project_path=path)


if __name__ == "__main__":
    cli()
