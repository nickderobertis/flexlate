import os
from pathlib import Path
from typing import Sequence, Optional, List, Dict, Any

from git import Repo

from flexlate.config_manager import ConfigManager
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import GitRepoDirtyException
from flexlate.finder.multi import MultiFinder
from flexlate.path_ops import make_all_dirs
from flexlate.render.multi import MultiRenderer
from flexlate.render.renderable import Renderable
from flexlate.template.base import Template
from flexlate.ext_git import (
    delete_tracked_files,
    stage_and_commit_all,
    merge_branch_into_current,
    checked_out_template_branch,
    checkout_template_branch,
    repo_has_merge_conflicts,
    assert_repo_is_in_clean_state,
)
from flexlate.template_data import TemplateData, merge_data
from flexlate.update.template import (
    TemplateUpdate,
    updates_with_updated_data,
)


class Updater:
    def update(
        self,
        repo: Repo,
        updates: Sequence[TemplateUpdate],
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        no_input: bool = False,
        renderer: MultiRenderer = MultiRenderer(),
        config_manager: ConfigManager = ConfigManager(),
    ):
        assert_repo_is_in_clean_state(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")

        out_path = Path(repo.working_dir)
        current_branch = repo.active_branch

        # Prepare the template branch, this is the branch that stores only the template files
        # Create it from the initial commit if it does not exist
        cwd = Path(os.getcwd())
        with checked_out_template_branch(repo, branch_name=template_branch_name):
            config_manager.update_templates(updates, project_root=out_path)
            renderables = config_manager.get_renderables(project_root=out_path)
            _create_cwd_and_directories_if_needed(
                cwd, [renderable.out_root for renderable in renderables]
            )
            updated_data = renderer.render(
                renderables, project_root=out_path, no_input=no_input
            )
            new_updates = updates_with_updated_data(updates, updated_data)
            config_manager.update_templates(new_updates, project_root=out_path)
            stage_and_commit_all(repo, _commit_message(renderables))

        # Now prepare the merged (output) branch, by merging the current
        # branch into it and then the template branch into it.
        checkout_template_branch(repo, merged_branch_name)
        # Update with changes from the main repo
        merge_branch_into_current(repo, current_branch.name)
        # Update with template changes
        merge_branch_into_current(repo, template_branch_name)

        if not repo_has_merge_conflicts(repo):
            # No conflicts, merge back into current branch
            current_branch.checkout()
            merge_branch_into_current(repo, merged_branch_name)

    def get_updates_for_templates(
        self,
        templates: Sequence[Template],
        data: Optional[Sequence[TemplateData]] = None,
        project_root: Path = Path("."),
        config_manager: ConfigManager = ConfigManager(),
    ) -> List[TemplateUpdate]:
        data = data or []
        all_updates = config_manager.get_no_op_updates(project_root=project_root)
        templates_by_name = {template.name: template for template in templates}
        out_updates: List[TemplateUpdate] = []
        for i, template in enumerate(templates):
            try:
                template_data = data[i]
            except IndexError:
                template_data = {}
            # TODO: more efficient algorithm for matching updates to templates
            for update in all_updates:
                if update.template.name in templates_by_name:
                    update.data = merge_data([template_data], [update.data or {}])[0]
                    update.template.version = template.version
                    update.template.path = template.path
                    out_updates.append(update)
        return out_updates

    def update_passed_templates_to_target_versions(
        self,
        templates: Sequence[Template],
        project_root: Path = Path("."),
        finder: MultiFinder = MultiFinder(),
        config_manager: ConfigManager = ConfigManager(),
    ):
        sources = config_manager.get_sources_for_templates(
            templates, project_root=project_root
        )
        templates_by_name = {template.name: template for template in templates}
        for source in sources:
            # TODO: Separate finding from updating the local version of the repo
            #  If the code failed after the find line but before updating the config,
            #  then the config would not match what is on the disk
            kwargs: Dict[str, Any] = {}
            if source.target_version:
                kwargs.update(version=source.target_version)
            new_template = finder.find(str(source.update_location), **kwargs)
            template = templates_by_name[source.name]
            if template.version != new_template.version:
                # Template needs to be upgraded
                # As finder already updates the local files, just update the template object
                template.version = new_template.version


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
