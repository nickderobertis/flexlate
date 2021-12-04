from pathlib import Path
from typing import Optional

from git import Repo

from flexlate.add_mode import AddMode
from flexlate.config import FlexlateConfig
from flexlate.config_manager import ConfigManager
from flexlate.exc import GitRepoDirtyException
from flexlate.ext_git import checked_out_template_branch, stage_and_commit_all
from flexlate.render.multi import MultiRenderer
from flexlate.template.base import Template
from flexlate.template_data import TemplateData
from flexlate.update.main import Updater
from flexlate.update.template import TemplateUpdate


class Adder:
    def add_template_source(
        self,
        template: Template,
        out_root: Path = Path("."),
        project_root: Path = Path("."),
        add_mode: AddMode = AddMode.LOCAL,
        config_manager: ConfigManager = ConfigManager(),
    ):
        config_path = _determine_config_path(out_root, project_root, add_mode)
        config_manager.add_template_source(
            template, config_path, project_root=project_root
        )

    def apply_template_and_add(
        self,
        repo: Repo,
        template: Template,
        data: Optional[TemplateData] = None,
        out_root: Path = Path("."),
        add_mode: AddMode = AddMode.LOCAL,
        branch_name: str = "flexlate-output",
        no_input: bool = False,
        config_manager: ConfigManager = ConfigManager(),
        updater: Updater = Updater(),
        renderer: MultiRenderer = MultiRenderer(),
    ):
        if repo.is_dirty(untracked_files=True):
            raise GitRepoDirtyException(
                "git working tree is not clean. Please commit, stash, or discard any changes first."
            )

        project_root = Path(repo.working_dir)
        config_path = _determine_config_path(out_root, project_root, add_mode)
        with checked_out_template_branch(repo, branch_name=branch_name):
            config_manager.add_applied_template(
                template, config_path, data=data, project_root=project_root
            )
            stage_and_commit_all(
                repo, _commit_message(template, out_root, project_root)
            )
        template_update = TemplateUpdate(
            template=template,
            config_location=config_path,
            index=config_manager.get_num_applied_templates_in_child_config(
                config_path, project_root=project_root
            ),
            data=data,
        )
        updater.update(
            repo,
            [template_update],
            branch_name=branch_name,
            no_input=no_input,
            renderer=renderer,
            config_manager=config_manager,
        )


def _determine_config_path(
    out_root: Path = Path("."),
    project_root: Path = Path("."),
    add_mode: AddMode = AddMode.LOCAL,
) -> Path:
    if add_mode == AddMode.USER:
        return FlexlateConfig._settings.config_location
    if add_mode == AddMode.PROJECT:
        return project_root / "flexlate.json"
    if add_mode == AddMode.LOCAL:
        return out_root / "flexlate.json"


def _commit_message(template: Template, out_root: Path, project_root: Path) -> str:
    relative_path = out_root.relative_to(project_root)
    return f"Applied template {template.name} to {relative_path}"
