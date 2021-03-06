import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from git import GitCommandError, Repo
from rich.prompt import Confirm

from flexlate.branch_update import (
    abort_merge_and_reset_flexlate_branches,
    prompt_to_fix_conflicts_and_reset_on_abort_return_aborted,
)
from flexlate.cli_utils import confirm_user
from flexlate.config_manager import ConfigManager
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import (
    MergeConflictsAndAbortException,
    TriedToCommitButNoChangesException,
)
from flexlate.ext_git import (
    abort_merge,
    assert_repo_is_in_clean_state,
    branch_exists,
    checkout_template_branch,
    fast_forward_branch_without_checkout,
    get_branch_sha,
    get_merge_conflict_diffs,
    merge_branch_into_current,
    repo_has_merge_conflicts,
    reset_branch_to_commit_without_checkout,
    restore_initial_commit_files,
    stage_and_commit_all,
    temp_repo_that_pushes_to_branch,
    update_local_branches_from_remote_without_checkout,
)
from flexlate.finder.multi import MultiFinder
from flexlate.logger import log
from flexlate.path_ops import (
    location_relative_to_new_parent,
    make_absolute_path_from_possibly_relative_to_another_path,
    make_all_dirs,
)
from flexlate.render.multi import MultiRenderer
from flexlate.render.renderable import Renderable
from flexlate.styles import (
    ACTION_REQUIRED_STYLE,
    ALERT_STYLE,
    INFO_STYLE,
    QUESTION_STYLE,
    SUCCESS_STYLE,
    print_styled,
    styled,
)
from flexlate.template.base import Template
from flexlate.template_data import TemplateData, merge_data
from flexlate.transactions.transaction import (
    FlexlateTransaction,
    create_transaction_commit_message,
)
from flexlate.update.template import TemplateUpdate, updates_with_updated_data


class Updater:
    def update(
        self,
        repo: Repo,
        updates: Sequence[TemplateUpdate],
        transaction: FlexlateTransaction,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        no_input: bool = False,
        abort_on_conflict: bool = False,
        cleanup: bool = True,
        full_rerender: bool = True,
        remote: str = "origin",
        renderer: MultiRenderer = MultiRenderer(),
        config_manager: ConfigManager = ConfigManager(),
    ):
        assert_repo_is_in_clean_state(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")

        project_root = Path(repo.working_dir)
        current_branch = repo.active_branch

        # Save the status of the flexlate branches. We may need to roll back to this state
        # if the user aborts the merge
        log.debug(
            f"Saving branch state before update for {merged_branch_name} and {template_branch_name}"
        )
        merged_branch_sha = get_branch_sha(repo, merged_branch_name)
        template_branch_sha = get_branch_sha(repo, template_branch_name)

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

        # Prepare the template branch, this is the branch that stores only the template files
        # Create it from the initial commit if it does not exist
        cwd = Path(os.getcwd())
        with temp_repo_that_pushes_to_branch(  # type: ignore
            repo,
            branch_name=template_branch_name,
            base_branch_name=base_template_branch_name,
            delete_tracked_files=full_rerender,
            remote=remote,
        ) as temp_repo:
            temp_project_root = Path(temp_repo.working_dir)  # type: ignore
            log.debug(
                f"Working in a temporary repo at {temp_project_root} to update template branch {template_branch_name}"
            )
            temp_updates = _move_update_config_locations_to_new_parent(
                updates, project_root, temp_project_root
            )
            # On first update, don't use template source path. This means that
            # the template paths will be absolute, so they can be loaded even though we are
            # working in a temp directory
            config_manager.update_templates(
                temp_updates,
                project_root=temp_project_root,
                use_template_source_path=False,
            )
            orig_renderables = (
                config_manager.get_all_renderables(
                    relative_to=project_root, project_root=temp_project_root
                )
                if full_rerender
                else config_manager.get_renderables_for_updates(
                    updates, project_root=project_root
                )
            )
            if full_rerender:
                print_styled(
                    f"Syncing changes in flexlate configs to output", INFO_STYLE
                )
            else:
                print_styled(
                    f"Updating {len(orig_renderables)} applied templates", INFO_STYLE
                )

            prompt_set_renderables = (
                _copy_renderables_skipping_prompts_if_not_in_updates(
                    orig_renderables, updates, project_root=project_root
                )
            )
            renderables = _move_renderable_out_roots_to_new_parent(
                prompt_set_renderables,
                project_root,
                temp_project_root,
            )

            _create_cwd_and_directories_if_needed(
                cwd, [renderable.out_root for renderable in renderables]
            )
            updated_data = renderer.render(
                renderables, project_root=temp_project_root, no_input=no_input
            )
            new_updates = updates_with_updated_data(
                updates,
                updated_data,
                renderables,
                project_root=project_root,
                render_root=temp_project_root,
            )
            new_temp_updates = _move_update_config_locations_to_new_parent(
                new_updates, project_root, temp_project_root
            )

            # For applied templates with local add mode, with corresponding template sources that
            # have a render_relative_root_in_output, may need to move the config
            rendered_temp_updates = config_manager.move_local_applied_templates_if_necessary_produce_new_updates(
                new_temp_updates,
                project_root=temp_project_root,
                orig_project_root=project_root,
                renderer=renderer,
            )

            # On second update, use template source path. This means that it will set the template
            # paths back to how they were originally (relative if needed), so that there will not be
            # unexpected changes from relative to absolute paths in the user configs
            config_manager.update_templates(
                rendered_temp_updates, project_root=temp_project_root
            )

            # Add back initial commit files if they have not been rendered from a template
            if full_rerender:
                restore_initial_commit_files(temp_repo)

            commit_message = create_transaction_commit_message(
                _commit_message(renderables), transaction
            )
            try:
                stage_and_commit_all(temp_repo, commit_message)
            except GitCommandError as e:
                if "nothing to commit, working tree clean" in str(e):
                    # This is expected if user tries to run update or sync when not needed
                    raise TriedToCommitButNoChangesException(
                        "update did not make any new changes"
                    ) from e
                # Unexpected exception, raise it
                raise e
            log.debug("Leaving temp directory")

        log.debug(f"Updating merged branch {merged_branch_name}")
        # Now prepare the merged (output) branch
        if not branch_exists(repo, merged_branch_name) and branch_exists(
            repo, base_merged_branch_name
        ):
            # If output feature branch doesn't exist but output main branch does,
            # start it from the main output branch
            log.debug(
                f"Fast forwarding {merged_branch_name} based on {base_merged_branch_name}"
            )
            fast_forward_branch_without_checkout(
                repo, merged_branch_name, base_merged_branch_name
            )

        # Now get the output branch updated by merging the current branch into it
        log.debug(f"Merging {current_branch.name} into {merged_branch_name}")
        # If the feature output branch exists, check it out
        # If the feature output branch doesn't exist:
        #  If the main output branch exists, start it from the main output branch
        #  If the main output branch doesn't exist, start it from the current branch
        checkout_template_branch(repo, merged_branch_name, base_merged_branch_name)
        merge_branch_into_current(repo, current_branch.name)

        # Update with template changes
        log.debug(f"Merging {template_branch_name} into {merged_branch_name}")
        merge_branch_into_current(repo, template_branch_name)

        if repo_has_merge_conflicts(repo):
            log.debug(f"Merge conflicts:\n{get_merge_conflict_diffs(repo)}")
            if abort_on_conflict:
                print_styled(
                    "Repo has merge conflicts after update, aborting due to abort_on_conflict=True",
                    ALERT_STYLE,
                )
                if cleanup:
                    abort_merge_and_reset_flexlate_branches(
                        repo,
                        current_branch,
                        merged_branch_sha=merged_branch_sha,
                        template_branch_sha=template_branch_sha,
                        merged_branch_name=merged_branch_name,
                        template_branch_name=template_branch_name,
                    )
                raise MergeConflictsAndAbortException

            # Need to wait for user to resolve merge conflicts
            aborted = prompt_to_fix_conflicts_and_reset_on_abort_return_aborted(
                repo,
                current_branch,
                merged_branch_sha,
                template_branch_sha,
                merged_branch_name,
                template_branch_name,
            )
            if aborted:
                raise MergeConflictsAndAbortException

        # No conflicts, merge back into current branch
        current_branch.checkout()
        merge_branch_into_current(repo, merged_branch_name)

        # Current working directory or out root may have been deleted if it was a remove operation
        # and there was nothing else in the folder (git does not save folders without files)
        ensure_exists_folders = [cwd]
        for renderable in orig_renderables:
            ensure_exists_folders.append(
                make_absolute_path_from_possibly_relative_to_another_path(
                    renderable.out_root, project_root
                )
            )
        for folder in ensure_exists_folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

        # Folder may have been deleted again while switching branches, so
        # need to set cwd again
        os.chdir(cwd)

        print_styled("Successfully updated template output", SUCCESS_STYLE)

    def get_updates_for_templates(
        self,
        templates: Sequence[Template],
        data: Optional[Sequence[TemplateData]] = None,
        project_root: Path = Path("."),
        config_manager: ConfigManager = ConfigManager(),
    ) -> List[TemplateUpdate]:
        data = data or []
        all_updates = config_manager.get_no_op_updates(project_root=project_root)
        out_updates: List[TemplateUpdate] = []
        for i, template in enumerate(templates):
            try:
                template_data = data[i]
            except IndexError:
                template_data = {}
            # TODO: more efficient algorithm for matching updates to templates
            for update in all_updates:
                if update.template.name == template.name:
                    update.data = merge_data([template_data], [update.data or {}])[0]
                    update.template.update_from_template(template)
                    out_updates.append(update)
        return out_updates

    def update_passed_templates_to_target_versions(
        self,
        templates: Sequence[Template],
        project_root: Path = Path("."),
        finder: MultiFinder = MultiFinder(),
        config_manager: ConfigManager = ConfigManager(),
    ):
        sources_with_templates = config_manager.get_sources_with_templates(
            templates, project_root=project_root
        )
        for source_with_templates in sources_with_templates:
            # TODO: Separate finding from updating the local version of the repo
            #  If the code failed after the find line but before updating the config,
            #  then the config would not match what is on the disk
            source = source_with_templates.source
            kwargs: Dict[str, Any] = {}
            if source.target_version:
                kwargs.update(version=source.target_version)
            for template in source_with_templates.templates:
                new_template = finder.find(str(source.update_location), **kwargs)
                # TODO: Create new templates rather than updating existing ones
                #  This would eliminate issues from partial updates of templates as new attributes are added.
                #  I think the logic is set up this way because order of the templates matters.
                if template.version != new_template.version:
                    # Template needs to be upgraded
                    # As finder already updates the local files, just update the template object
                    template.update_from_template(new_template)


def _commit_message(renderables: Sequence[Renderable]) -> str:
    message = "Update flexlate templates\n\n"
    for renderable in renderables:
        template = renderable.template
        message += f"{template.name}: {template.version}\n"
    return message


def _create_cwd_and_directories_if_needed(cwd: Path, directories: Sequence[Path]):
    make_all_dirs([cwd])

    # Folder may have been deleted again while switching branches, so
    # need to set cwd again
    os.chdir(cwd)

    make_all_dirs(directories)


def _move_update_config_locations_to_new_parent(
    updates: Sequence[TemplateUpdate], orig_parent: Path, new_parent: Path
) -> List[TemplateUpdate]:
    cwd = Path(os.getcwd())
    return [
        update.copy(
            update=dict(
                config_location=location_relative_to_new_parent(
                    update.config_location, orig_parent, new_parent, cwd
                )
            )
        )
        for update in updates
    ]


def _move_renderable_out_roots_to_new_parent(
    renderables: Sequence[Renderable], orig_parent: Path, new_parent: Path
) -> List[Renderable]:
    return [
        renderable.copy(
            update=dict(
                out_root=location_relative_to_new_parent(
                    renderable.out_root, orig_parent, new_parent, orig_parent
                )
            )
        )
        for renderable in renderables
    ]


def _copy_renderables_skipping_prompts_if_not_in_updates(
    renderables: Sequence[Renderable],
    updates: Sequence[TemplateUpdate],
    project_root: Path,
) -> List[Renderable]:
    update_renderables = [
        update.to_renderable(project_root=project_root) for update in updates
    ]
    return [
        renderable.copy(update=dict(skip_prompts=renderable not in update_renderables))
        for renderable in renderables
    ]
