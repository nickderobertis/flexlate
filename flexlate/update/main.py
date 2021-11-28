import os
import shutil
from pathlib import Path
from typing import Sequence, Optional, List

from git import Repo

from flexlate.config_manager import ConfigManager
from flexlate.exc import GitRepoDirtyException
from flexlate.render.multi import MultiRenderer
from flexlate.template.base import Template
from flexlate.types import TemplateData
from flexlate.ext_git import (
    checkout_template_branch,
    delete_tracked_files,
    stage_and_commit_all,
    merge_branch_into_current,
)


class Updater:
    def update(
        self,
        repo: Repo,
        templates: Sequence[Template],
        data: Optional[Sequence[TemplateData]] = None,
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
        orig_branch = repo.active_branch
        checkout_template_branch(repo, branch_name=branch_name)
        delete_tracked_files(repo)
        previous_data = config_manager.get_data_for_templates(templates, project_root=out_path)
        input_data = _merge_data(data or [], previous_data)
        updated_data = renderer.render(templates, data=input_data, out_path=out_path, no_input=no_input)
        config_manager.update_applied_templates(templates, updated_data, project_root=out_path)
        stage_and_commit_all(repo, _commit_message(templates))
        orig_branch.checkout()
        merge_branch_into_current(repo, branch_name)


def _commit_message(templates: Sequence[Template]) -> str:
    message = "Update flexlate templates\n\n"
    for template in templates:
        message += f"{template.name}: {template.version}\n"
    return message


def _merge_data(overrides: Sequence[TemplateData], defaults: Sequence[TemplateData]) -> List[TemplateData]:
    out_data: List[TemplateData] = []
    for i, default_data in enumerate(defaults):
        try:
            override_data = overrides[i]
        except IndexError:
            override_data = {}
        out_data.append({**default_data, **override_data})
    return out_data