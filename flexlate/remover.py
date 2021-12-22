import os
from pathlib import Path

from git import Repo

from flexlate.add_mode import AddMode
from flexlate.branch_update import modify_files_via_branches_and_temp_repo
from flexlate.config_manager import (
    ConfigManager,
    determine_config_path_from_roots_and_add_mode,
)
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.ext_git import assert_repo_is_in_clean_state
from flexlate.path_ops import (
    location_relative_to_new_parent,
)


class Remover:
    def remove_template_source(
        self,
        repo: Repo,
        template_name: str,
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
            # No need to use git if was added for user
            config_manager.remove_template_source(
                template_name, config_path=config_path, project_root=project_root
            )
            return

        modify_files_via_branches_and_temp_repo(
            lambda temp_path: config_manager.remove_template_source(
                template_name,
                location_relative_to_new_parent(
                    config_path, project_root, temp_path, Path(os.getcwd())
                ),
                project_root=temp_path,
            ),
            repo,
            _remove_template_source_commit_message(
                template_name, out_root, Path(repo.working_dir)
            ),
            out_root,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
        )


def _remove_template_source_commit_message(
    template_name: str, out_root: Path, project_root: Path
) -> str:
    relative_path = out_root.absolute().relative_to(project_root)
    return f"Removed template source {template_name} from {relative_path}"
