from typing import Optional

from git import Repo, GitCommandError

from flexlate.branch_update import (
    get_flexlate_branch_name_for_feature_branch,
    abort_merge_and_reset_flexlate_branches,
)
from flexlate.cli_utils import confirm_user
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.ext_git import (
    fast_forward_branch_without_checkout,
    temp_repo_that_pushes_to_branch,
    repo_has_merge_conflicts,
    get_branch_sha,
    delete_local_branch,
    merge_branch_into_current,
)
from flexlate.styles import (
    print_styled,
    INFO_STYLE,
    ACTION_REQUIRED_STYLE,
    styled,
    QUESTION_STYLE,
    ALERT_STYLE,
    SUCCESS_STYLE,
)


class Merger:
    def merge_flexlate_branches(
        self,
        repo: Repo,
        branch_name: Optional[str] = None,
        delete: bool = True,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    ):
        feature_branch = branch_name or repo.active_branch.name
        flexlate_feature_merged_branch_name = (
            get_flexlate_branch_name_for_feature_branch(
                feature_branch, merged_branch_name
            )
        )
        flexlate_feature_template_branch_name = (
            get_flexlate_branch_name_for_feature_branch(
                feature_branch, template_branch_name
            )
        )

        # Save the status of the flexlate branches. We may need to roll back to this state
        # if the user aborts the merge
        current_branch = repo.active_branch
        merged_branch_sha = get_branch_sha(repo, merged_branch_name)
        template_branch_sha = get_branch_sha(repo, template_branch_name)

        print_styled(
            f"Merging {flexlate_feature_template_branch_name} to {template_branch_name}",
            INFO_STYLE,
        )
        try:
            fast_forward_branch_without_checkout(
                repo, template_branch_name, flexlate_feature_template_branch_name
            )
        except GitCommandError as e:
            if not "non-fast-forward" in str(e):
                # Got some unexpected git error, raise it
                raise e
            # Could not fast forward. Must do a merge in a temp repo and have user resolve any conflicts
            with temp_repo_that_pushes_to_branch(  # type: ignore
                repo,
                branch_name=template_branch_name,
                base_branch_name=template_branch_name,
                additional_branches=(flexlate_feature_template_branch_name,),
                copy_current_configs=False,
            ) as temp_repo:
                merge_branch_into_current(temp_repo, flexlate_feature_template_branch_name)  # type: ignore
                if repo_has_merge_conflicts(temp_repo):
                    print_styled(
                        f"Encountered merge conflicts while merging "
                        f"{flexlate_feature_template_branch_name} into {template_branch_name}",
                        INFO_STYLE,
                    )
                    print_styled(
                        f"Flexlate uses a temporary repo for this merge. "
                        f"Please resolve conflicts in {temp_repo.working_dir}",  # type: ignore
                        ACTION_REQUIRED_STYLE,
                    )
                    handled_conflicts = confirm_user(
                        styled(
                            f"Successfully handled conflicts in {temp_repo.working_dir}? n to abort",  # type: ignore
                            QUESTION_STYLE,
                        )
                    )
                    if not handled_conflicts:
                        # Have only done work in a temp dir so far, so can just abort
                        print_styled("Aborting merge.", ALERT_STYLE)
                        return
        print_styled(
            f"Successfully merged {flexlate_feature_template_branch_name} to {template_branch_name}",
            SUCCESS_STYLE,
        )

        # Now merge the merged branch in the main repo
        try:
            fast_forward_branch_without_checkout(
                repo, merged_branch_name, flexlate_feature_merged_branch_name
            )
        except GitCommandError as e:
            if not "non-fast-forward" in str(e):
                # Got some unexpected git error, raise it
                raise e
            # Could not fast forward. Must do a merge and have user resolve any conflicts
            merged_branch = repo.branches[merged_branch_name]  # type: ignore
            merged_branch.checkout()
            # First merge the template branch, so that user won't have to resolve the same conflict
            # from there again
            merge_branch_into_current(repo, template_branch_name)
            # Now merge the feature merged branch to get new changes from feature branch
            merge_branch_into_current(repo, flexlate_feature_merged_branch_name)
            if repo_has_merge_conflicts(repo):
                print_styled(
                    f"Encountered merge conflicts while merging "
                    f"{flexlate_feature_template_branch_name} into {template_branch_name}",
                    INFO_STYLE,
                )
                print_styled(f"Please resolve the conflicts", ACTION_REQUIRED_STYLE)
                handled_conflicts = confirm_user(
                    styled("Successfully handled conflicts? n to abort", QUESTION_STYLE)
                )
                if not handled_conflicts:
                    # Time ot abort, but need to reset the state of the branches
                    print_styled("Aborting merge.", ALERT_STYLE)
                    abort_merge_and_reset_flexlate_branches(
                        repo,
                        current_branch,
                        merged_branch_sha=merged_branch_sha,
                        template_branch_sha=template_branch_sha,
                        merged_branch_name=merged_branch_name,
                        template_branch_name=template_branch_name,
                    )

                    return
            current_branch.checkout()

        print_styled(
            f"Successfully merged {flexlate_feature_merged_branch_name} to {merged_branch_name}",
            SUCCESS_STYLE,
        )

        if not delete:
            return

        # Handle delete
        print_styled(
            f"Deleting flexlate feature branches {flexlate_feature_template_branch_name} and {flexlate_feature_merged_branch_name}",
            INFO_STYLE,
        )
        delete_local_branch(repo, flexlate_feature_template_branch_name)
        delete_local_branch(repo, flexlate_feature_merged_branch_name)
        print_styled(f"Successfully deleted flexlate feature branches", SUCCESS_STYLE)
