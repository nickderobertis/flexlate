from typing import Optional

from git import Repo

from flexlate.branch_update import get_flexlate_branch_name_for_feature_branch
from flexlate.constants import DEFAULT_TEMPLATE_BRANCH_NAME, DEFAULT_MERGED_BRANCH_NAME
from flexlate.ext_git import branch_exists, push_to_remote
from flexlate.styles import print_styled, ALERT_STYLE, INFO_STYLE, SUCCESS_STYLE


class Pusher:
    def push_main_flexlate_branches(
        self,
        repo: Repo,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    ):
        ...

    def push_feature_flexlate_branches(
        self,
        repo: Repo,
        feature_branch: Optional[str] = None,
        remote: str = "origin",
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    ):
        branch_name = feature_branch or repo.active_branch.name
        feature_merged_branch_name = get_flexlate_branch_name_for_feature_branch(
            branch_name, merged_branch_name
        )
        feature_template_branch_name = get_flexlate_branch_name_for_feature_branch(
            branch_name, template_branch_name
        )

        for branch in [feature_template_branch_name, feature_merged_branch_name]:
            if not branch_exists(repo, branch):
                print_styled(
                    f"Could not push branch {branch} as it does not exist", ALERT_STYLE
                )
                return

        print_styled(
            f"Pushing {feature_template_branch_name} and {feature_merged_branch_name} to remote {remote}",
            INFO_STYLE,
        )
        push_to_remote(repo, feature_template_branch_name, remote_name=remote)
        push_to_remote(repo, feature_merged_branch_name, remote_name=remote)
        print_styled("Successfully pushed branches to remote", SUCCESS_STYLE)
