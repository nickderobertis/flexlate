import os
from pathlib import Path
from typing import Optional

from git import Repo

from flexlate.add_mode import AddMode, get_expanded_out_root
from flexlate.branch_update import modify_files_via_branches_and_temp_repo
from flexlate.config_manager import (
    ConfigManager,
    determine_config_path_from_roots_and_add_mode,
)
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.ext_git import (
    assert_repo_is_in_clean_state,
)
from flexlate.path_ops import (
    location_relative_to_new_parent,
)
from flexlate.render.multi import MultiRenderer
from flexlate.template.base import Template
from flexlate.template_data import TemplateData
from flexlate.update.main import Updater
from flexlate.update.template import TemplateUpdate


class Adder:
    def add_template_source(
        self,
        repo: Repo,
        template: Template,
        target_version: Optional[str] = None,
        out_root: Path = Path("."),
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        add_mode: AddMode = AddMode.LOCAL,
        config_manager: ConfigManager = ConfigManager(),
    ):
        assert_repo_is_in_clean_state(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")

        config_path = determine_config_path_from_roots_and_add_mode(
            out_root, Path(repo.working_dir), add_mode
        )
        project_root = Path(repo.working_dir)

        if add_mode == AddMode.USER:
            # No need to use git if adding for user
            config_manager.add_template_source(
                template,
                config_path,
                target_version=target_version,
                project_root=Path(repo.working_dir),  # type: ignore
            )
            return

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
            _add_template_source_commit_message(
                template, out_root, Path(repo.working_dir)
            ),
            out_root,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
        )

    def apply_template_and_add(
        self,
        repo: Repo,
        template: Template,
        data: Optional[TemplateData] = None,
        out_root: Path = Path("."),
        add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        no_input: bool = False,
        config_manager: ConfigManager = ConfigManager(),
        updater: Updater = Updater(),
        renderer: MultiRenderer = MultiRenderer(),
    ):
        assert_repo_is_in_clean_state(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")

        project_root = Path(repo.working_dir)
        config_path = determine_config_path_from_roots_and_add_mode(
            out_root, project_root, add_mode
        )
        expanded_out_root = get_expanded_out_root(out_root, project_root, add_mode)

        if add_mode == AddMode.USER:
            # No need to commit config changes for user
            config_manager.add_applied_template(
                template,
                config_path,
                data=data,
                project_root=project_root,
                out_root=expanded_out_root,
            )
        else:
            # Commit changes for local and project
            modify_files_via_branches_and_temp_repo(
                lambda temp_path: config_manager.add_applied_template(
                    template,
                    location_relative_to_new_parent(
                        config_path, project_root, temp_path, Path(os.getcwd())
                    ),
                    data=data,
                    project_root=temp_path,
                    out_root=expanded_out_root,
                ),
                repo,
                _add_template_commit_message(
                    template, out_root, Path(repo.working_dir)
                ),
                out_root,
                merged_branch_name=merged_branch_name,
                template_branch_name=template_branch_name,
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
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
            no_input=no_input,
            renderer=renderer,
            config_manager=config_manager,
        )

    def init_project_and_add_to_branches(
        self,
        repo: Repo,
        default_add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        user: bool = False,
        config_manager: ConfigManager = ConfigManager(),
    ):
        assert_repo_is_in_clean_state(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")

        path = Path(repo.working_dir)

        if user:
            # Simply init the project for the user
            config_manager.add_project(
                path=path,
                default_add_mode=default_add_mode,
                user=user,
                merged_branch_name=merged_branch_name,
                template_branch_name=template_branch_name,
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
            ),
            repo,
            "Initialized flexlate project",
            path,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
        )


def _add_template_commit_message(
    template: Template, out_root: Path, project_root: Path
) -> str:
    relative_path = out_root.absolute().relative_to(project_root)
    return f"Applied template {template.name} to {relative_path}"


def _add_template_source_commit_message(
    template: Template, out_root: Path, project_root: Path
) -> str:
    relative_path = out_root.absolute().relative_to(project_root)
    return f"Added template source {template.name} to {relative_path}"
