import os
from pathlib import Path

from git import Repo

from flexlate.add_mode import AddMode, get_expanded_out_root
from flexlate.branch_update import modify_files_via_branches_and_temp_repo
from flexlate.config_manager import (
    ConfigManager,
    determine_config_path_from_roots_and_add_mode,
)
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import CannotRemoveAppliedTemplateException
from flexlate.ext_git import (
    assert_repo_is_in_clean_state,
    update_local_branches_from_remote_without_checkout,
)
from flexlate.path_ops import (
    location_relative_to_new_parent,
)
from flexlate.render.multi import MultiRenderer
from flexlate.styles import console, styled, INFO_STYLE, print_styled, SUCCESS_STYLE
from flexlate.transactions.transaction import (
    FlexlateTransaction,
    create_transaction_commit_message,
)
from flexlate.update.main import Updater


class Remover:
    def remove_template_source(
        self,
        repo: Repo,
        template_name: str,
        transaction: FlexlateTransaction,
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

        with console.status(styled("Removing template source...", INFO_STYLE)):
            print_styled(f"Removing template source {template_name}", INFO_STYLE)
            if add_mode == AddMode.USER:
                # No need to use git if was added for user
                config_manager.remove_template_source(
                    template_name, config_path=config_path, project_root=project_root
                )
                return

            commit_message = create_transaction_commit_message(
                _remove_template_source_commit_message(
                    template_name, out_root, Path(repo.working_dir)
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
                lambda temp_path: config_manager.remove_template_source(
                    template_name,
                    location_relative_to_new_parent(
                        config_path, project_root, temp_path, Path(os.getcwd())
                    ),
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
                f"Successfully removed template source {template_name}", SUCCESS_STYLE
            )

    def remove_applied_template_and_output(
        self,
        repo: Repo,
        template_name: str,
        transaction: FlexlateTransaction,
        out_root: Path = Path("."),
        add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        remote: str = "origin",
        config_manager: ConfigManager = ConfigManager(),
        updater: Updater = Updater(),
        renderer: MultiRenderer = MultiRenderer(),
    ):
        assert_repo_is_in_clean_state(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")

        project_root = Path(repo.working_dir)
        template = config_manager.get_template_by_name(
            template_name, project_root=project_root
        )

        # Determine location of config
        # Need to get renderable to render path in case it is templated
        # TODO: can use get all renderables
        renderables = config_manager.get_renderables_for_updates(
            config_manager.get_no_op_updates(project_root=project_root),
            project_root=project_root,
        )
        if len(renderables) == 0:
            raise CannotRemoveAppliedTemplateException(
                f"Cannot find any applied template with name {template_name} "
                f"because there are no applied templates"
            )
        renderable = renderables[0]
        new_relative_out_root = Path(
            renderer.render_string(
                str(template.render_relative_root_in_output), renderable
            )
        )
        full_local_config_out_root = out_root / new_relative_out_root
        config_path = determine_config_path_from_roots_and_add_mode(
            full_local_config_out_root, project_root, add_mode
        )

        expanded_out_root = get_expanded_out_root(
            out_root, project_root, template.render_relative_root_in_output, add_mode
        )

        with console.status(styled("Removing applied template...", INFO_STYLE)):
            print_styled(
                f"Removing applied template {template_name} at {expanded_out_root.resolve()}",
                INFO_STYLE,
            )
            if add_mode == AddMode.USER:
                # No need to commit config changes for user
                config_manager.remove_applied_template(
                    template_name,
                    config_path,
                    project_root=project_root,
                    out_root=expanded_out_root,
                    orig_project_root=project_root,
                )
            else:
                # Commit changes for local and project
                commit_message = create_transaction_commit_message(
                    _remove_applied_template_commit_message(
                        template_name, out_root, Path(repo.working_dir)
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
                    lambda temp_path: config_manager.remove_applied_template(
                        template_name,
                        location_relative_to_new_parent(
                            config_path, project_root, temp_path, Path(os.getcwd())
                        ),
                        project_root=temp_path,
                        out_root=expanded_out_root,
                        orig_project_root=project_root,
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

            updater.update(
                repo,
                [],
                transaction,
                merged_branch_name=merged_branch_name,
                base_merged_branch_name=base_merged_branch_name,
                template_branch_name=template_branch_name,
                base_template_branch_name=base_template_branch_name,
                no_input=True,
                remote=remote,
                renderer=renderer,
                config_manager=config_manager,
            )
            print_styled(
                f"Successfully removed applied template {template_name} at {expanded_out_root.resolve()}",
                SUCCESS_STYLE,
            )


def _remove_template_source_commit_message(
    template_name: str, out_root: Path, project_root: Path
) -> str:
    relative_path = out_root.absolute().relative_to(project_root)
    return f"Removed template source {template_name} from {relative_path}"


def _remove_applied_template_commit_message(
    template_name: str, out_root: Path, project_root: Path
) -> str:
    relative_path = out_root.absolute().relative_to(project_root)
    return f"Removed template {template_name} from {relative_path}"
