import os
import shutil
import tempfile
import time
from copy import deepcopy
from pathlib import Path
from typing import Optional

from git import Repo
from rich.prompt import Prompt

from flexlate.add_mode import AddMode, get_expanded_out_root
from flexlate.branch_update import modify_files_via_branches_and_temp_repo
from flexlate.config import TemplateSource
from flexlate.config_manager import (
    ConfigManager,
    determine_config_path_from_roots_and_add_mode,
)
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import TemplateSourceWithNameAlreadyExistsException
from flexlate.ext_git import (
    assert_repo_is_in_clean_state,
    stage_and_commit_all,
    update_local_branches_from_remote_without_checkout,
)
from flexlate.path_ops import (
    location_relative_to_new_parent,
)
from flexlate.render.multi import MultiRenderer
from flexlate.styles import SUCCESS_STYLE, INFO_STYLE, console, styled, print_styled
from flexlate.syncer import Syncer
from flexlate.template.base import Template
from flexlate.template_data import TemplateData
from flexlate.transactions.transaction import (
    FlexlateTransaction,
    create_transaction_commit_message,
)
from flexlate.update.main import Updater
from flexlate.update.template import TemplateUpdate


class Adder:
    def add_template_source(
        self,
        repo: Repo,
        template: Template,
        transaction: FlexlateTransaction,
        target_version: Optional[str] = None,
        out_root: Path = Path("."),
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        add_mode: AddMode = AddMode.LOCAL,
        remote: str = "origin",
        config_manager: ConfigManager = ConfigManager(),
    ):
        assert_repo_is_in_clean_state(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")

        config_path = determine_config_path_from_roots_and_add_mode(
            out_root, Path(repo.working_dir), add_mode
        )
        project_root = Path(repo.working_dir)

        if config_manager.template_source_exists(
            template.name, project_root=project_root
        ):
            raise TemplateSourceWithNameAlreadyExistsException(
                f"There is an existing template source with the name {template.name}. "
                f"To add this one, give it a custom name or remove the existing one"
            )

        if not template.path.is_absolute() and not (
            config_path.parent.resolve() == Path(os.getcwd())
        ):
            # Relative path, if the config output location is different than the
            # current directory, need to adjust the path to be relative to
            # the config output location

            # Don't overwrite existing template
            template = deepcopy(template)
            # Make template path relative to its config file rather than current directory
            template.path = Path(
                os.path.relpath(template.path.resolve(), config_path.parent.resolve())
            )

        with console.status(print_styled("Adding template source...", INFO_STYLE)):
            print_styled(
                f"Adding template source {template.name} from {template.git_url or template.path}",
                INFO_STYLE,
            )

            if add_mode == AddMode.USER:
                # No need to use git if adding for user
                config_manager.add_template_source(
                    template,
                    config_path,
                    target_version=target_version,
                    project_root=Path(repo.working_dir),  # type: ignore
                )
                return

            commit_message = create_transaction_commit_message(
                _add_template_source_commit_message(
                    template, out_root, Path(repo.working_dir)
                ),
                transaction,
            )

            # Ensure that all flexlate branches are up to date from remote before working on them
            update_local_branches_from_remote_without_checkout(
                repo,
                [
                    base_merged_branch_name,
                    merged_branch_name,
                    base_template_branch_name,
                    template_branch_name,
                ],
                remote=remote,
            )

            # Local or project config, add in git
            modify_files_via_branches_and_temp_repo(
                lambda temp_path: config_manager.add_template_source(
                    template,
                    location_relative_to_new_parent(
                        config_path, project_root, temp_path, Path(os.getcwd())
                    ),
                    target_version=target_version,
                    project_root=temp_path,
                ),
                repo,
                commit_message,
                out_root,
                merged_branch_name=merged_branch_name,
                base_merged_branch_name=base_merged_branch_name,
                template_branch_name=template_branch_name,
                base_template_branch_name=base_template_branch_name,
                remote=remote,
            )

            print_styled(
                f"Sucessfully added template source {template.name}", INFO_STYLE
            )

    def apply_template_and_add(
        self,
        repo: Repo,
        template: Template,
        transaction: FlexlateTransaction,
        data: Optional[TemplateData] = None,
        out_root: Path = Path("."),
        add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        no_input: bool = False,
        remote: str = "origin",
        config_manager: ConfigManager = ConfigManager(),
        updater: Updater = Updater(),
        renderer: MultiRenderer = MultiRenderer(),
    ):
        assert_repo_is_in_clean_state(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")

        project_root = Path(repo.working_dir)
        full_local_config_out_root = out_root / template.render_relative_root_in_output
        config_path = determine_config_path_from_roots_and_add_mode(
            full_local_config_out_root, project_root, add_mode
        )
        expanded_out_root = get_expanded_out_root(
            out_root, project_root, template.render_relative_root_in_output, add_mode
        )

        # Get path it is being rendered at to display to user
        render_path = expanded_out_root
        if not expanded_out_root.is_absolute():
            render_path = (project_root / expanded_out_root).resolve()

        print_styled(
            f"Applying template {template.name} to {render_path}",
            INFO_STYLE,
        )

        if add_mode == AddMode.USER:
            # No need to commit config changes for user
            config_manager.add_applied_template(
                template,
                config_path,
                add_mode,
                data=data,
                project_root=project_root,
                out_root=expanded_out_root,
            )
        else:
            # Commit changes for local and project
            commit_message = create_transaction_commit_message(
                _add_template_commit_message(
                    template, out_root, Path(repo.working_dir)
                ),
                transaction,
            )

            # Ensure that all flexlate branches are up to date from remote before working on them
            update_local_branches_from_remote_without_checkout(
                repo,
                [
                    base_merged_branch_name,
                    merged_branch_name,
                    base_template_branch_name,
                    template_branch_name,
                ],
                remote=remote,
            )

            modify_files_via_branches_and_temp_repo(
                lambda temp_path: config_manager.add_applied_template(
                    template,
                    location_relative_to_new_parent(
                        config_path, project_root, temp_path, Path(os.getcwd())
                    ),
                    add_mode,
                    data=data,
                    project_root=temp_path,
                    out_root=expanded_out_root,
                ),
                repo,
                commit_message,
                out_root,
                merged_branch_name=merged_branch_name,
                base_merged_branch_name=base_merged_branch_name,
                template_branch_name=template_branch_name,
                base_template_branch_name=base_template_branch_name,
                remote=remote,
            )
        template_update = TemplateUpdate(
            template=template,
            config_location=config_path,
            index=config_manager.get_num_applied_templates_in_child_config(
                config_path, project_root=project_root
            )
            - 1,
            data=data,
        )
        updater.update(
            repo,
            [template_update],
            transaction,
            merged_branch_name=merged_branch_name,
            base_merged_branch_name=base_merged_branch_name,
            template_branch_name=template_branch_name,
            base_template_branch_name=base_template_branch_name,
            no_input=no_input,
            full_rerender=False,
            remote=remote,
            renderer=renderer,
            config_manager=config_manager,
        )
        print_styled(
            f"Successfully applied template {template.name} to {render_path}",
            SUCCESS_STYLE,
        )

    def init_project_and_add_to_branches(
        self,
        repo: Repo,
        default_add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        user: bool = False,
        remote: str = "origin",
        config_manager: ConfigManager = ConfigManager(),
    ):
        assert_repo_is_in_clean_state(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")

        path = Path(repo.working_dir)

        with console.status(styled("Initializing...", INFO_STYLE)):
            print_styled(
                f"Initializing flexlate project with default add mode "
                f"{default_add_mode.value} and user={user} in "
                f"{Path(repo.working_dir).resolve()}",
                INFO_STYLE,
            )

            if user:
                # Simply init the project for the user
                config_manager.add_project(
                    path=path,
                    default_add_mode=default_add_mode,
                    user=user,
                    merged_branch_name=merged_branch_name,
                    template_branch_name=template_branch_name,
                    remote=remote,
                )
                return

            # Config resides in project, so add it via branches
            modify_files_via_branches_and_temp_repo(
                lambda temp_path: config_manager.add_project(
                    path=temp_path,
                    default_add_mode=default_add_mode,
                    user=user,
                    merged_branch_name=merged_branch_name,
                    template_branch_name=template_branch_name,
                    remote=remote,
                ),
                repo,
                "Initialized flexlate project",
                path,
                merged_branch_name=merged_branch_name,
                base_merged_branch_name=merged_branch_name,
                template_branch_name=template_branch_name,
                base_template_branch_name=template_branch_name,
                remote=remote,
            )

        print_styled(
            f"Finished initializing flexlate project",
            SUCCESS_STYLE,
        )

    def init_project_from_template_source_path(
        self,
        template: Template,
        transaction: FlexlateTransaction,
        path: Path = Path("."),
        target_version: Optional[str] = None,
        data: Optional[TemplateData] = None,
        default_folder_name: str = "project",
        default_add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        remote: str = "origin",
        no_input: bool = False,
        config_manager: ConfigManager = ConfigManager(),
        updater: Updater = Updater(),
        renderer: MultiRenderer = MultiRenderer(),
        syncer: Syncer = Syncer(),
    ) -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            repo = Repo.init(temp_dir)

            def sync():
                syncer.sync_local_changes_to_flexlate_branches(
                    repo,
                    transaction,
                    merged_branch_name=merged_branch_name,
                    base_merged_branch_name=merged_branch_name,
                    template_branch_name=template_branch_name,
                    base_template_branch_name=template_branch_name,
                    no_input=True,
                    remote=remote,
                    updater=updater,
                    renderer=renderer,
                    config_manager=config_manager,
                )

            temp_file = temp_path / "README.md"
            temp_file.touch()
            stage_and_commit_all(repo, "Initial commit")
            self.init_project_and_add_to_branches(
                repo,
                default_add_mode=default_add_mode,
                merged_branch_name=merged_branch_name,
                template_branch_name=template_branch_name,
                user=False,
                remote=remote,
                config_manager=config_manager,
            )
            self.add_template_source(
                repo,
                template,
                transaction,
                target_version=target_version,
                out_root=temp_path,
                merged_branch_name=merged_branch_name,
                template_branch_name=template_branch_name,
                add_mode=AddMode.LOCAL,
                remote=remote,
                config_manager=config_manager,
            )
            self.apply_template_and_add(
                repo,
                template,
                transaction,
                data=data,
                out_root=temp_path,
                add_mode=AddMode.LOCAL,
                merged_branch_name=merged_branch_name,
                template_branch_name=template_branch_name,
                no_input=no_input,
                remote=remote,
                config_manager=config_manager,
                updater=updater,
                renderer=renderer,
            )
            if template.render_relative_root_in_output == Path("."):
                output_folder = temp_path
                folder_name = default_folder_name
                if not no_input:
                    folder_name = Prompt.ask(
                        "Output folder name? (this template does not provide one)",
                        default=default_folder_name,
                    )
                if not len(temp_file.read_text()):
                    os.remove(temp_file)
                    stage_and_commit_all(repo, "Remove temporary file")
            else:
                # Output renders in a subdirectory. Find that directory
                renderables = config_manager.get_all_renderables(project_root=temp_path)
                if len(renderables) != 1:
                    raise ValueError(
                        "there should only be one renderable in the init-from process"
                    )
                renderable = renderables[0]
                new_relative_out_root = Path(
                    renderer.render_string(
                        str(template.render_relative_root_in_output), renderable
                    )
                )
                output_folder = (temp_path / new_relative_out_root).resolve()
                folder_name = new_relative_out_root.name

                # Move template source and project config into output directory
                orig_config_path = temp_path / "flexlate.json"
                new_config_path = temp_path / new_relative_out_root / "flexlate.json"
                config_manager.move_template_source(
                    template.name,
                    orig_config_path,
                    new_config_path,
                    project_root=temp_path,
                )

                orig_project_config_path = temp_path / "flexlate-project.json"
                new_project_config_path = (
                    temp_path / new_relative_out_root / "flexlate-project.json"
                )
                shutil.move(str(orig_project_config_path), str(new_project_config_path))

                # Move .git folder into output directory
                git_folder = temp_path / ".git"
                new_git_folder = temp_path / new_relative_out_root / ".git"
                shutil.move(str(git_folder), str(new_git_folder))
                # Reassign repo now that it has moved
                repo = Repo(temp_path / new_relative_out_root)

                stage_and_commit_all(
                    repo, "Move flexlate config and remove temporary file"
                )
                sync()

            final_out_path = path / folder_name
            shutil.copytree(output_folder, final_out_path)
            repo = Repo(final_out_path)

            # Now update template source path that was previously relative to temp directory
            if template.git_url is None and not Path(template.path).is_absolute():
                cwd = Path(os.getcwd())

                def move_source_path_to_be_relative_to_destination(
                    source: TemplateSource,
                ):
                    source.path = str(
                        os.path.relpath(
                            (cwd / Path(template.template_source_path)).resolve(),
                            final_out_path,
                        )
                    )

                config_manager.update_template_sources(
                    [template.name],
                    move_source_path_to_be_relative_to_destination,
                    project_root=final_out_path,
                )
                stage_and_commit_all(
                    repo,
                    "Move template source path to match permanent destination of project",
                )
                sync()

            return folder_name


def _add_template_commit_message(
    template: Template, out_root: Path, project_root: Path
) -> str:
    relative_path = out_root.absolute().relative_to(project_root)
    return f"Applied template {template.name} to {relative_path}"


def _move_applied_template_config_message(
    template: Template, out_root: Path, project_root: Path
) -> str:
    relative_path = out_root.absolute().relative_to(project_root)
    return f"Moved config for {template.name} to {relative_path}"


def _add_template_source_commit_message(
    template: Template, out_root: Path, project_root: Path
) -> str:
    relative_path = out_root.absolute().relative_to(project_root)
    return f"Added template source {template.name} to {relative_path}"
