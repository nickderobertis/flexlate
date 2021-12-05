import os
from pathlib import Path
from typing import Optional, Callable

from git import Repo

from flexlate.add_mode import AddMode
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
        expanded_out_root = (
            out_root.absolute() if add_mode == AddMode.USER else out_root
        )

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
            # TODO: restructure the current path logic into _add_operation_via_branches
            #  as it will also be needed for other operations.
            # Commit changes for local and project
            cwd = Path(os.getcwd())
            absolute_out_root = out_root.absolute()
            def make_dirs_add_applied_template():
                # Need to ensure that both cwd and out root exist on the template branch
                for p in [cwd, absolute_out_root]:
                    if not p.exists():
                        p.mkdir(parents=True)
                # If cwd was deleted when switching branches, need to navigate back there
                # or os.getcwd will throw a FileNotExistsError (which also breaks path.absolute())
                os.chdir(cwd)

                config_manager.add_applied_template(
                    template,
                    config_path,
                    data=data,
                    project_root=project_root,
                    out_root=expanded_out_root,
                )

            _add_operation_via_branches(
                make_dirs_add_applied_template,
                repo,
                _add_template_commit_message(
                    template, out_root, Path(repo.working_dir)
                ),
                merged_branch_name=merged_branch_name,
                template_branch_name=template_branch_name,
            )

            # Folder may have been deleted again while switching branches, so
            # need to set cwd again
            os.chdir(cwd)

        template_update = TemplateUpdate(
            template=template,
            config_location=config_path,
            index=config_manager.get_num_applied_templates_in_child_config(
                config_path, project_root=project_root
            ) - 1,
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
    merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
    template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
):
    current_branch = repo.active_branch

    # Update the template only branch with the new template
    with checked_out_template_branch(repo, branch_name=template_branch_name):
        add_operation()
        stage_and_commit_all(repo, commit_message)

    # Bring the change into the merged branch
    with checked_out_template_branch(repo, branch_name=merged_branch_name):
        # Update with changes from the main repo
        merge_branch_into_current(repo, current_branch.name)
        # Update with the new template
        merge_branch_into_current(repo, template_branch_name)

    # Merge back into current branch
    merge_branch_into_current(repo, merged_branch_name)


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
