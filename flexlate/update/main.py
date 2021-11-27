import os
import shutil
from pathlib import Path
from typing import Sequence, Optional

from git import Repo

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
        data: Optional[TemplateData] = None,
        renderer: MultiRenderer = MultiRenderer(),
        branch_name: str = "flexlate-output",
    ):
        if repo.is_dirty(untracked_files=True):
            raise GitRepoDirtyException(
                "git working tree is not clean. Please commit, stash, or discard any changes first."
            )

        out_path = Path(repo.working_dir)
        orig_branch = repo.active_branch
        checkout_template_branch(repo, branch_name=branch_name)
        delete_tracked_files(repo)
        renderer.render(templates, data=data, out_path=out_path)
        stage_and_commit_all(repo, _commit_message(templates))
        orig_branch.checkout()
        merge_branch_into_current(repo, branch_name)


def _commit_message(templates: Sequence[Template]) -> str:
    message = "Update flexlate templates\n\n"
    for template in templates:
        message += f"{template.name}: {template.version}\n"
    return message
