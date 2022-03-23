from pathlib import Path
from typing import Optional, List

import typer

from flexlate.add_mode import AddMode
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import MergeConflictsAndAbortException
from flexlate.logger import log
from flexlate.main import Flexlate

cli = typer.Typer()

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
QUIET_DOC = "Suppress CLI output except for prompts"
REMOTE_DOC = "The name of the remote repository"
PUSH_REMOTE_DOC = (
    "The name of the remote repository to push to, defaults to project config remote"
)
TEMPLATE_SOURCE_NAME_DOC = (
    "The name of the template. It must match a name in template sources"
)

TEMPLATE_ROOT_OPTION = typer.Option(
    Path("."),
    "--root",
    "-r",
    help=TEMPLATE_ROOT_DOC,
    show_default=False,
)
TEMPLATE_ROOT_ARGUMENT = typer.Argument(
    Path("."),
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
VERSION_ARGUMENT = typer.Argument(
    None,
    help=TARGET_VERSION_DOC,
)
QUIET_OPTION = typer.Option(False, "--quiet", "-q", show_default=False)
PROJECT_PATH_ARGUMENT = typer.Argument(Path("."), help=PROJECT_PATH_DOC)
PROJECT_PATH_OPTION = typer.Option(Path("."), help=PROJECT_PATH_DOC)
REMOTE_OPTION = typer.Option("origin", "--remote", "-r", help=REMOTE_DOC)
PUSH_REMOTE_OPTION = typer.Option(
    None, "--remote", "-r", help=REMOTE_DOC, show_default=False
)
TEMPLATE_SOURCE_NAME_ARGUMENT = typer.Argument(
    ...,
    help=TEMPLATE_SOURCE_NAME_DOC,
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
    quiet: bool = QUIET_OPTION,
):
    """
    Adds a new template source, so that files can be generated from it
    """
    app = Flexlate(quiet=quiet)
    app.add_template_source(
        path,
        name=name,
        target_version=version,
        template_root=template_root,
        add_mode=add_mode,
    )


@add_cli.command(name="output")
def generate_applied_template(
    name: str = TEMPLATE_SOURCE_NAME_ARGUMENT,
    template_root: Path = TEMPLATE_ROOT_ARGUMENT,
    add_mode: Optional[AddMode] = ADD_MODE_OPTION,
    no_input: bool = NO_INPUT_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Applies a template to a given location, and stores it in config so it can be updated
    """
    app = Flexlate(quiet=quiet)
    app.apply_template_and_add(
        name,
        out_root=template_root,
        add_mode=add_mode,
        no_input=no_input,
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
    quiet: bool = QUIET_OPTION,
):
    app = Flexlate(quiet=quiet)
    app.remove_template_source(template_name, template_root=template_root)


@remove_cli.command(name="output")
def remove_template_output(
    template_name: str = typer.Argument(
        ...,
        help="The name of the template source corresponding to "
        "the applied template output to remove",
    ),
    template_root: Path = TEMPLATE_ROOT_ARGUMENT,
    quiet: bool = QUIET_OPTION,
):
    app = Flexlate(quiet=quiet)
    app.remove_applied_template_and_output(template_name, out_root=template_root)


cli.add_typer(remove_cli, name="remove")


@cli.command(name="init")
def init_project(
    path: Path = PROJECT_PATH_ARGUMENT,
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
    remote: str = REMOTE_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Initializes a flexlate project. This must be run before other commands
    """
    app = Flexlate(quiet=quiet)
    app.init_project(
        path,
        default_add_mode=default_add_mode,
        merged_branch_name=merged_branch_name,
        template_branch_name=template_branch_name,
        user=user,
        remote=remote,
    )


@cli.command(name="init-from")
def init_project_from(
    template_path: str = typer.Argument(
        ...,
        help=f"A template source path to initialize the project from. {TEMPLATE_SOURCE_EXTRA_DOC}",
    ),
    path: Path = PROJECT_PATH_ARGUMENT,
    version: Optional[str] = VERSION_OPTION,
    folder_name: str = typer.Option(
        "project",
        "--folder-name",
        "-f",
        help="The name of the outputted folder. This only applies on templates that don't set the name of the folder (Copier)",
    ),
    no_input: bool = NO_INPUT_OPTION,
    quiet: bool = QUIET_OPTION,
    default_add_mode: AddMode = typer.Option(
        AddMode.LOCAL,
        "--add-mode",
        "-a",
        help=ADD_MODE_DOC,
        case_sensitive=False,
        show_choices=True,
    ),
    remote: str = REMOTE_OPTION,
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
    app = Flexlate(quiet=quiet)
    app.init_project_from(
        template_path,
        path,
        template_version=version,
        default_folder_name=folder_name,
        no_input=no_input,
        default_add_mode=default_add_mode,
        remote=remote,
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
    abort_on_conflict: bool = typer.Option(
        False,
        "--abort",
        "-a",
        help="Automatically abort the update if a merge conflict is encountered. Useful in combination with --no-input for CI systems",
    ),
    quiet: bool = QUIET_OPTION,
    path: Path = PROJECT_PATH_OPTION,
):
    """
    Updates applied templates in the project to the newest versions
    available that still satisfy source target versions
    """
    app = Flexlate(quiet=quiet)
    try:
        app.update(
            names=names,
            no_input=no_input,
            abort_on_conflict=abort_on_conflict,
            project_path=path,
        )
        log.debug("Exiting with code 0")
        return
    except MergeConflictsAndAbortException:
        # There is already output explaining the situation to the user prior to
        # raising the exception, so only need to exit with the correct code
        log.debug("Exiting with code 1")
        exit(1)


@cli.command(name="undo")
def undo(
    num_operations: int = typer.Argument(
        1,
        help="Number of flexlate operations to undo",
    ),
    path: Path = PROJECT_PATH_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Undoes the last flexlate operation, like ctrl/cmd + z for flexlate.
    Note that this modifies the git history, discarding the last commits.
    It has protections against deleting user commits but you should only
    use this on a feature branch.
    """
    app = Flexlate(quiet=quiet)
    app.undo(num_operations=num_operations, project_path=path)


@cli.command(name="sync")
def sync(
    path: Path = PROJECT_PATH_ARGUMENT,
    prompt: bool = typer.Option(
        False,
        "--prompt",
        "-p",
        help="Pass to enable answering template prompts",
        show_default=False,
    ),
    quiet: bool = QUIET_OPTION,
):
    """
    Syncs manual changes to the flexlate branches, and updates templates
    accordingly. This is useful if you want to move or modify flexlate configs
    after they are created, but there is no command in the CLI for it.
    This is currently the way to update template versions until there is a
    specific command for it: manually change the version and run sync.

    Note: Be sure to commit your changes before running sync
    """
    app = Flexlate(quiet=quiet)
    app.sync(prompt=prompt, project_path=path)


@cli.command(name="merge")
def merge(
    branch_name: Optional[str] = typer.Argument(
        None,
        help="Optional name of feature branch for which to merge "
        "corresponding flexlate branches. Defaults to current branch",
    ),
    delete: bool = typer.Option(
        True,
        "--no-delete",
        "-n",
        help="Pass to prevent deleting feature flexlate branches after merge",
        show_default=False,
    ),
    path: Path = PROJECT_PATH_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Merges feature flexlate branches into the main flexlate branches

    Feature flexlate branches should be merged into main flexlate branches when
    the corresponding feature branch is merged into the repo's main branch. This
    command provides a convenient way to do so.
    """
    app = Flexlate(quiet=quiet)
    app.merge_flexlate_branches(branch_name, delete=delete, project_path=path)


push_cli = typer.Typer(help="Push flexlate branches to remote repositories")


@push_cli.command("main")
def push_main(
    remote: Optional[str] = PUSH_REMOTE_OPTION,
    path: Path = PROJECT_PATH_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Pushes main flexlate branches to remote
    """
    app = Flexlate(quiet=quiet)
    app.push_main_flexlate_branches(remote, project_path=path)


@push_cli.command("feature")
def push_feature(
    feature_branch: Optional[str] = typer.Argument(
        None,
        help="The name of the branch used while running the flexlate operations for which we want to push the corresponding flexlate branches",
    ),
    remote: str = REMOTE_OPTION,
    path: Path = PROJECT_PATH_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Pushes main flexlate branches to remote
    """
    app = Flexlate(quiet=quiet)
    app.push_feature_flexlate_branches(feature_branch, remote, project_path=path)


cli.add_typer(push_cli, name="push")


@cli.command(name="check")
def check(
    names: Optional[List[str]] = typer.Argument(
        None,
        help="Optional names of templates to updates. Defaults to all templates",
        show_default=False,
    ),
    path: Path = PROJECT_PATH_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Checks whether there are any updates available for the current template sources

    Displays a tabular output of the templates that need to be updated. It will also
    exist with code 1 when updates are available so that it is easy to use in scripting.
    """
    app = Flexlate(quiet=quiet)
    check_result = app.check(names=names, project_path=path)
    if check_result.has_updates:
        exit(1)


@cli.command(name="bootstrap")
def bootstrap(
    template_path: str = typer.Argument(
        ...,
        help=f"A template source path to bootstrap the project from. {TEMPLATE_SOURCE_EXTRA_DOC}",
    ),
    path: Path = PROJECT_PATH_ARGUMENT,
    version: Optional[str] = VERSION_OPTION,
    no_input: bool = NO_INPUT_OPTION,
    quiet: bool = QUIET_OPTION,
    default_add_mode: AddMode = typer.Option(
        AddMode.LOCAL,
        "--add-mode",
        "-a",
        help=ADD_MODE_DOC,
        case_sensitive=False,
        show_choices=True,
    ),
    remote: str = REMOTE_OPTION,
    merged_branch_name: str = typer.Option(
        DEFAULT_MERGED_BRANCH_NAME, help=MERGED_BRANCH_DOC
    ),
    template_branch_name: str = typer.Option(
        DEFAULT_TEMPLATE_BRANCH_NAME,
        help=TEMPLATE_BRANCH_DOC,
    ),
):
    """
    Takes an existing project that was already generated by another tool such as Cookiecutter or
    Copier and sets it up as a Flexlate project.
    """
    app = Flexlate(quiet=quiet)
    app.bootstrap_flexlate_init_from_existing_template(
        template_path,
        path,
        template_version=version,
        no_input=no_input,
        default_add_mode=default_add_mode,
        remote=remote,
        merged_branch_name=merged_branch_name,
        template_branch_name=template_branch_name,
    )


cli.add_typer(push_cli, name="push")
config_cli = typer.Typer(help="Modify Flexlate configs via CLI")


@config_cli.command("target")
def update_template_source_target_version(
    name: str = TEMPLATE_SOURCE_NAME_ARGUMENT,
    version: Optional[str] = VERSION_ARGUMENT,
    path: Path = PROJECT_PATH_OPTION,
    add_mode: Optional[AddMode] = ADD_MODE_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Updates a target version for a template source. If no version is passed,
    it will remove the targeting so it will always update.
    """
    app = Flexlate(quiet=quiet)
    app.update_template_source_target_version(
        name, target_version=version, add_mode=add_mode, project_path=path
    )


cli.add_typer(config_cli, name="config")

if __name__ == "__main__":
    cli()
