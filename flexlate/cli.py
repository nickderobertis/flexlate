from pathlib import Path
from typing import Optional, List

import typer

from flexlate import exc
from flexlate.add_mode import AddMode
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.error_handler import simple_output_for_exceptions
from flexlate.exc import MergeConflictsAndAbortException
from flexlate.get_version import get_flexlate_version
from flexlate.logger import log
from flexlate.main import Flexlate
from flexlate.styles import print_styled, INFO_STYLE

MAIN_DOC = """
fxt is a CLI tool to manage project and file generator templates.

[See the Flexlate documentation](
https://nickderobertis.github.io/flexlate/
) for more information.
""".strip()

cli = typer.Typer(help=MAIN_DOC)

ADD_CLI_DOC = """
Add template sources and generate new projects and files from existing template sources

See the
[user guide on adding new templates within an existing project](
https://nickderobertis.github.io/flexlate/tutorial/get-started/add-to-project.html
) for more details.
""".strip()

add_cli = typer.Typer(help=ADD_CLI_DOC)

TEMPLATE_ROOT_DOC = (
    "The root directory the template should be rendered from, defaults to current"
)
ADD_MODE_DOC = (
    "Local adds the config to the template root, project adds it to the project "
    "config (which may also be template root), and user adds it to the user config"
)
NO_INPUT_DOC = "Whether to proceed without any input from the user (skip all prompts)"
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
NO_INPUT_OPTION = typer.Option(
    False, "--no-input", "-n", show_default=False, help=NO_INPUT_DOC
)
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
QUIET_OPTION = typer.Option(False, "--quiet", "-q", show_default=False, help=QUIET_DOC)
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


@cli.callback(invoke_without_command=True)
def pre_execute(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        show_default=False,
        help="Show Flexlate version and exit",
    )
):
    # Support printing version and then existing with fxt --version
    if version:
        version_number = get_flexlate_version()
        print_styled(version_number, INFO_STYLE)
        exit(0)


@add_cli.command(name="source")
@simple_output_for_exceptions(
    exc.GitRepoDirtyException, exc.TemplateSourceWithNameAlreadyExistsException
)
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
    Adds a new template source, so that files can be generated from it.

    See the
    [user guide on adding new templates within an existing project](
    https://nickderobertis.github.io/flexlate/tutorial/get-started/add-to-project.html
    ) for more details.
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
@simple_output_for_exceptions(
    exc.GitRepoDirtyException, exc.TemplateNotRegisteredException
)
def generate_applied_template(
    name: str = TEMPLATE_SOURCE_NAME_ARGUMENT,
    template_root: Path = TEMPLATE_ROOT_ARGUMENT,
    add_mode: Optional[AddMode] = ADD_MODE_OPTION,
    no_input: bool = NO_INPUT_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Applies a template to a given location, and stores it in config so it can be updated

    See the
    [user guide on adding new templates within an existing project](
    https://nickderobertis.github.io/flexlate/tutorial/get-started/add-to-project.html
    ) for more details.
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
@simple_output_for_exceptions(exc.GitRepoDirtyException)
def remove_template_source(
    template_name: str = typer.Argument(
        ..., help="The name of the template source to remove"
    ),
    template_root: Path = TEMPLATE_ROOT_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Removes a template source, so that files can no longer be generated from it.
    """
    app = Flexlate(quiet=quiet)
    app.remove_template_source(template_name, template_root=template_root)


@remove_cli.command(name="output")
@simple_output_for_exceptions(exc.GitRepoDirtyException)
def remove_template_output(
    template_name: str = typer.Argument(
        ...,
        help="The name of the template source corresponding to "
        "the applied template output to remove",
    ),
    template_root: Path = TEMPLATE_ROOT_ARGUMENT,
    quiet: bool = QUIET_OPTION,
):
    """
    Removes an applied template output
    """
    app = Flexlate(quiet=quiet)
    app.remove_applied_template_and_output(template_name, out_root=template_root)


cli.add_typer(remove_cli, name="remove")


@cli.command(name="init")
@simple_output_for_exceptions(exc.GitRepoDirtyException)
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

    See the user guide on
    [adding templates within an existing project](
    https://nickderobertis.github.io/flexlate/tutorial/get-started/add-to-project.html
    ) for more details.
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

    Note that this will also create a new folder and initialize a git repository in it
    before adding the Flexlate output.

    See the user guide on
    [creating a new project with Flexlate](
    https://nickderobertis.github.io/flexlate/tutorial/get-started/new-project.html
    ) for more information.
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
@simple_output_for_exceptions(exc.GitRepoDirtyException)
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
    no_cleanup: bool = typer.Option(
        False,
        "--no-cleanup",
        "-c",
        help="Do not abort the merge or reset branch state upon abort. Note that this flag is ignored if --abort is not passed",
    ),
    quiet: bool = QUIET_OPTION,
    path: Path = PROJECT_PATH_OPTION,
):
    """
    Updates applied templates in the project to the newest versions
    available that still satisfy source target versions

    See the user guide on
    [updating templates](
    https://nickderobertis.github.io/flexlate/tutorial/updating.html
    ) for more information.
    """
    app = Flexlate(quiet=quiet)
    try:
        app.update(
            names=names,
            no_input=no_input,
            abort_on_conflict=abort_on_conflict,
            no_cleanup=no_cleanup,
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
@simple_output_for_exceptions(exc.GitRepoDirtyException)
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

    See the user guide on
    [undoing Flexlate operations](
    https://nickderobertis.github.io/flexlate/tutorial/undoing.html
    ) for more information.
    """
    app = Flexlate(quiet=quiet)
    app.undo(num_operations=num_operations, project_path=path)


@cli.command(name="sync")
@simple_output_for_exceptions(exc.GitRepoDirtyException, exc.UnnecessarySyncException)
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
    accordingly.

    This is useful if you want to move or modify flexlate configs
    after they are created, but there is no command in the CLI for it.

    Note: Be sure to commit your changes before running sync

    See the user guide on
    [making arbitrary changes](
    https://nickderobertis.github.io/flexlate/tutorial/arbitrary-changes.html
    ) for more information.
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

    See the user guide on
    [saving Flexlate updates](
    https://nickderobertis.github.io/flexlate/tutorial/saving.html
    ), especially
    [the section about locally merging branches](
    https://nickderobertis.github.io/flexlate/tutorial/saving.html#locally-merging-branches
    ), for more information.
    """
    app = Flexlate(quiet=quiet)
    app.merge_flexlate_branches(branch_name, delete=delete, project_path=path)


PUSH_DOC = """
Push Flexlate branches to remote repositories.

See the user guide on
[saving Flexlate updates](
https://nickderobertis.github.io/flexlate/tutorial/saving.html
) for more information.
""".strip()

push_cli = typer.Typer(help=PUSH_DOC)


@push_cli.command("main")
def push_main(
    remote: Optional[str] = PUSH_REMOTE_OPTION,
    path: Path = PROJECT_PATH_OPTION,
    quiet: bool = QUIET_OPTION,
):
    """
    Pushes main Flexlate branches to remote

    See the user guide on
    [saving Flexlate updates](
    https://nickderobertis.github.io/flexlate/tutorial/saving.html
    ), especially
    [the section about pushing with a local workflow](
    https://nickderobertis.github.io/flexlate/tutorial/saving.html#push-your-flexlate-main-branch-changes
    ), for more information.
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
    Pushes feature Flexlate branches to remote

    See the user guide on
    [saving Flexlate updates](
    https://nickderobertis.github.io/flexlate/tutorial/saving.html
    ), especially
    [the section about pushing changes with a PR workflow](
    https://nickderobertis.github.io/flexlate/tutorial/saving.html#push-your-flexlate-feature-branch-changes
    ), for more information.
    """
    app = Flexlate(quiet=quiet)
    app.push_feature_flexlate_branches(feature_branch, remote, project_path=path)


cli.add_typer(push_cli, name="push")


@cli.command(name="check")
@simple_output_for_exceptions(exc.TemplateNotRegisteredException)
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

    See the user guide on
    [updating templates](
    https://nickderobertis.github.io/flexlate/tutorial/updating.html
    ), especially
    [the section about checking for updates](
    https://nickderobertis.github.io/flexlate/tutorial/updating.html#checking-for-updates
    ), for more information.
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
    Sets up a Flexlate project from an existing project that was already generated by
    another tool such as Cookiecutter or Copier.

    See the user guide on
    [adding Flexlate to a project already generated from a template](
    https://nickderobertis.github.io/flexlate/tutorial/get-started/existing-project.html
    ) for more information.
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
    Updates a target version for a template source.

    If no version is passed, it will remove the targeting so it will always update.

    See the user guide on
    [updating templates](
    https://nickderobertis.github.io/flexlate/tutorial/updating.html
    ), especially
    [the section about changing target version](
    https://nickderobertis.github.io/flexlate/tutorial/updating.html#change-target-version
    ), for more information.
    """
    app = Flexlate(quiet=quiet)
    app.update_template_source_target_version(
        name, target_version=version, add_mode=add_mode, project_path=path
    )


cli.add_typer(config_cli, name="config")

if __name__ == "__main__":
    cli()
