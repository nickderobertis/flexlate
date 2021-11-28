from pathlib import Path
from typing import Sequence, Optional, List

from git import Repo

from flexlate.config_manager import ConfigManager
from flexlate.exc import GitRepoDirtyException
from flexlate.render.multi import MultiRenderer
from flexlate.template.base import Template
from flexlate.ext_git import (
    delete_tracked_files,
    stage_and_commit_all,
    merge_branch_into_current,
    checked_out_template_branch,
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
        branch_name: str = "flexlate-output",
        no_input: bool = False,
        renderer: MultiRenderer = MultiRenderer(),
        config_manager: ConfigManager = ConfigManager(),
    ):
        if repo.is_dirty(untracked_files=True):
            raise GitRepoDirtyException(
                "git working tree is not clean. Please commit, stash, or discard any changes first."
            )

        out_path = Path(repo.working_dir)
        with checked_out_template_branch(repo, branch_name=branch_name):
            config_manager.update_applied_templates(updates, project_root=out_path)
            templates, data = config_manager.get_templates_with_data(
                project_root=out_path
            )
            # TODO: shouldn't delete files, just overwrite
            delete_tracked_files(repo)
            updated_data = renderer.render(
                templates, data=data, out_path=out_path, no_input=no_input
            )
            new_updates = updates_with_updated_data(updates, updated_data)
            config_manager.update_applied_templates(new_updates, project_root=out_path)
            stage_and_commit_all(repo, _commit_message(templates))
        merge_branch_into_current(repo, branch_name)

    def get_updates_for_templates(
        self,
        templates: Sequence[Template],
        data: Optional[Sequence[TemplateData]],
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
                    out_updates.append(update)
        return out_updates


def _commit_message(templates: Sequence[Template]) -> str:
    message = "Update flexlate templates\n\n"
    for template in templates:
        message += f"{template.name}: {template.version}\n"
    return message
