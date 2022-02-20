from typing import Optional, Sequence

from git import Repo

from flexlate.branch_update import get_flexlate_branch_name_for_feature_branch
from flexlate.constants import DEFAULT_TEMPLATE_BRANCH_NAME, DEFAULT_MERGED_BRANCH_NAME
from flexlate.ext_git import branch_exists, push_to_remote
from flexlate.styles import print_styled, ALERT_STYLE, INFO_STYLE, SUCCESS_STYLE


class Pusher:
    def push_main_flexlate_branches(
        self,
        repo: Repo,
        remote: str = "origin",
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    ):
        _push_branches_to_remote(
            repo, [template_branch_name, merged_branch_name], remote=remote
        )

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
        _push_branches_to_remote(
            repo,
            [feature_template_branch_name, feature_merged_branch_name],
            remote=remote,
        )


def _push_branches_to_remote(
    repo: Repo, branch_names: Sequence[str], remote: str = "origin"
):
    for branch in branch_names:
        if not branch_exists(repo, branch):
            print_styled(
                f"Could not push branch {branch} as it does not exist", ALERT_STYLE
            )
            return
    and_branches = " and ".join(branch_names)
    print_styled(
        f"Pushing {and_branches} to remote {remote}",
        INFO_STYLE,
    )
    for branch in branch_names:
        push_to_remote(repo, branch, remote_name=remote)
    print_styled("Successfully pushed branches to remote", SUCCESS_STYLE)
