import os
from pathlib import Path
from typing import Sequence, Optional, List, Dict, Any

from git import Repo

from flexlate.config_manager import ConfigManager
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.finder.multi import MultiFinder
from flexlate.path_ops import make_all_dirs, location_relative_to_new_parent
from flexlate.render.multi import MultiRenderer
from flexlate.render.renderable import Renderable
from flexlate.template.base import Template
from flexlate.ext_git import (
    stage_and_commit_all,
    merge_branch_into_current,
    checkout_template_branch,
    repo_has_merge_conflicts,
    assert_repo_is_in_clean_state,
    temp_repo_that_pushes_to_branch,
    fast_forward_branch_without_checkout,
)
from flexlate.template_data import TemplateData, merge_data
from flexlate.update.template import (
    TemplateUpdate,
    updates_with_updated_data,
)
from tests.dirutils import display_contents_of_all_files_in_folder


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
        with temp_repo_that_pushes_to_branch(  # type: ignore
            repo, branch_name=template_branch_name, delete_tracked_files=True
        ) as temp_repo:
            temp_out_path = Path(temp_repo.working_dir)  # type: ignore
            temp_updates = _move_update_config_locations_to_new_parent(
                updates, out_path, temp_out_path
            )
            # On first update, don't use template source path. This means that
            # the template paths will be absolute, so they can be loaded even though we are
            # working in a temp directory
            config_manager.update_templates(
                temp_updates, project_root=temp_out_path, use_template_source_path=False
            )
            renderables = _move_renderable_out_roots_to_new_parent(
                config_manager.get_renderables(project_root=temp_out_path),
                out_path,
                temp_out_path,
            )

            _create_cwd_and_directories_if_needed(
                cwd, [renderable.out_root for renderable in renderables]
            )
            updated_data = renderer.render(
                renderables, project_root=temp_out_path, no_input=no_input
            )
            new_updates = updates_with_updated_data(temp_updates, updated_data)
            # On second update, use template source path. This means that it will set the template
            # paths back to how they were originally (relative if needed), so that there will not be
            # unexpected changes from relative to absolute paths in the user configs
            config_manager.update_templates(new_updates, project_root=temp_out_path)
            stage_and_commit_all(temp_repo, _commit_message(renderables))

        # Now prepare the merged (output) branch, by merging the current
        # branch into it and then the template branch into it.
        # Update with changes from the main repo
        fast_forward_branch_without_checkout(
            repo, merged_branch_name, current_branch.name
        )
        # Update with template changes
        checkout_template_branch(repo, merged_branch_name)
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
                template.path = new_template.path


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
    renderbales: Sequence[Renderable], orig_parent: Path, new_parent: Path
) -> List[Renderable]:
    return [
        renderable.copy(
            update=dict(
                out_root=location_relative_to_new_parent(
                    renderable.out_root, orig_parent, new_parent, orig_parent
                )
            )
        )
        for renderable in renderbales
    ]
