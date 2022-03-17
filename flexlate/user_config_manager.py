from pathlib import Path
from typing import Optional

from git import Repo

from flexlate.add_mode import AddMode
from flexlate.branch_update import modify_files_via_branches_and_temp_repo
from flexlate.config_manager import ConfigManager
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.transactions.transaction import (
    create_transaction_commit_message,
    FlexlateTransaction,
)


class UserConfigManager:
    """
    A higher-level version of the config manager that also works with flexlate branches

    ConfigManager is the lower-level version that does not care about branches
    """

    def update_template_source_target_version(
        self,
        name: str,
        target_version: Optional[str],
        repo: Repo,
        transaction: FlexlateTransaction,
        project_path: Path = Path("."),
        add_mode: Optional[AddMode] = None,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        remote: str = "origin",
        config_manager: ConfigManager = ConfigManager(),
    ):

        if add_mode == AddMode.USER:
            # No need to use git if adding for user
            config_manager.update_template_source_version(
                name, target_version=target_version, project_root=project_path
            )
            return

        commit_message = create_transaction_commit_message(
            _update_target_version_commit_message(name, target_version),
            transaction,
        )

        # Local or project config, add in git
        modify_files_via_branches_and_temp_repo(
            lambda temp_path: config_manager.update_template_source_version(
                name,
                target_version=target_version,
                project_root=temp_path,
            ),
            repo,
            commit_message,
            project_path,
            merged_branch_name=merged_branch_name,
            base_merged_branch_name=base_merged_branch_name,
            template_branch_name=template_branch_name,
            base_template_branch_name=base_template_branch_name,
            remote=remote,
        )


def _update_target_version_commit_message(
    name: str, target_version: Optional[str]
) -> str:
    display_target_version: str = str(target_version)
    if target_version is None:
        display_target_version = "null"
    return (
        f"Changed target version for template source {name} to {display_target_version}"
    )
