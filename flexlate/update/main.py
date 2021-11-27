import os
import shutil
from pathlib import Path
from typing import Sequence, Optional

from git import Repo

from flexlate.render.multi import MultiRenderer
from flexlate.template.base import Template
from flexlate.types import TemplateData
from flexlate.update.ext_git import (
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
        out_path = Path(repo.working_dir)
        # TODO: check if git repo and clean working directory, if not, exit
        orig_branch = repo.active_branch
        checkout_template_branch(repo, branch_name=branch_name)
        delete_tracked_files(repo)
        renderer.render(templates, data=data, out_path=out_path)
        # TODO: determine old and new version of template, put new template version in message
        stage_and_commit_all(repo, "Update template")
        orig_branch.checkout()
        merge_branch_into_current(repo, branch_name)
