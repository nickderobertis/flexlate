import os
from pathlib import Path
from typing import Optional, Callable

from git import Repo

from flexlate.add_mode import AddMode, get_expanded_out_root
from flexlate.config import FlexlateConfig
from flexlate.config_manager import ConfigManager
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import GitRepoDirtyException
from flexlate.ext_git import (
    checked_out_template_branch,
    stage_and_commit_all,
    merge_branch_into_current,
    assert_repo_is_in_clean_state,
)
from flexlate.path_ops import make_func_that_creates_cwd_and_out_root_before_running
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

        config_path = _determine_config_path(out_root, Path(repo.working_dir), add_mode)

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
        _add_operation_via_branches(
            lambda: config_manager.add_template_source(
                template,
                config_path,
                target_version=target_version,
                project_root=Path(repo.working_dir),  # type: ignore
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
        config_path = _determine_config_path(out_root, project_root, add_mode)
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
            _add_operation_via_branches(
                lambda: config_manager.add_applied_template(
                    template,
                    config_path,
                    data=data,
                    project_root=project_root,
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
        _add_operation_via_branches(
            lambda: config_manager.add_project(
                path=path,
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


def _determine_config_path(
    out_root: Path = Path("."),
    project_root: Path = Path("."),
    add_mode: AddMode = AddMode.LOCAL,
) -> Path:
    if add_mode == AddMode.USER:
        return FlexlateConfig._settings.config_location
    if add_mode == AddMode.PROJECT:
        return project_root / "flexlate.json"
    if add_mode == AddMode.LOCAL:
        return out_root / "flexlate.json"
    raise ValueError(f"unexpected add mode {add_mode}")


def _add_operation_via_branches(
    add_operation: Callable[[], None],
    repo: Repo,
    commit_message: str,
    out_root: Path,
    merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
    template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
):
    cwd = os.getcwd()
    current_branch = repo.active_branch

    make_dirs_add_operation = make_func_that_creates_cwd_and_out_root_before_running(
        out_root, add_operation
    )

    # Update the template only branch with the new template
    with checked_out_template_branch(repo, branch_name=template_branch_name):
        make_dirs_add_operation()
        stage_and_commit_all(repo, commit_message)

    # Bring the change into the merged branch
    with checked_out_template_branch(repo, branch_name=merged_branch_name):
        # Update with changes from the main repo
        merge_branch_into_current(repo, current_branch.name)
        # Update with the new template
        merge_branch_into_current(repo, template_branch_name)

    # Merge back into current branch
    merge_branch_into_current(repo, merged_branch_name)

    # Folder may have been deleted again while switching branches, so
    # need to set cwd again
    os.chdir(cwd)


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
