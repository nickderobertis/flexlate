from pathlib import Path
from typing import Optional, List

from git import Repo

from flexlate.adder import Adder
from flexlate.add_mode import AddMode
from flexlate.config_manager import ConfigManager
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.finder.multi import MultiFinder
from flexlate.render.multi import MultiRenderer
from flexlate.template.base import Template
from flexlate.template_data import TemplateData
from flexlate.update.main import Updater


class Flexlate:
    def __init__(
        self,
        adder: Adder = Adder(),
        config_manager: ConfigManager = ConfigManager(),
        finder: MultiFinder = MultiFinder(),
        renderer: MultiRenderer = MultiRenderer(),
        updater: Updater = Updater(),
    ):
        self.adder = adder
        self.config_manager = config_manager
        self.finder = finder
        self.renderer = renderer
        self.updater = updater

    def init_project(
        self,
        path: Path = Path("."),
        default_add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        user: bool = False,
    ):
        repo = Repo(path)
        self.adder.init_project_and_add_to_branches(
            repo,
            default_add_mode=default_add_mode,
            user=user,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
        )

    def add_template_source(
        self,
        path: str,
        name: Optional[str] = None,
        target_version: Optional[str] = None,
        template_root: Path = Path("."),
        add_mode: Optional[AddMode] = None,
    ):
        project_config = self.config_manager.load_project_config(template_root)
        add_mode = add_mode or project_config.default_add_mode
        template = self.finder.find(path, version=target_version)
        if name:
            template.name = name
        repo = Repo(project_config.path)
        self.adder.add_template_source(
            repo,
            template,
            target_version=target_version,
            out_root=template_root,
            merged_branch_name=project_config.merged_branch_name,
            template_branch_name=project_config.template_branch_name,
            add_mode=add_mode,
            config_manager=self.config_manager,
        )

    def apply_template_and_add(
        self,
        name: str,
        data: Optional[TemplateData] = None,
        out_root: Path = Path("."),
        add_mode: Optional[AddMode] = None,
        no_input: bool = False,
    ):
        project_config = self.config_manager.load_project_config(out_root)
        add_mode = add_mode or project_config.default_add_mode
        template = self.config_manager.get_template_by_name(
            name, project_root=project_config.path
        )
        repo = Repo(project_config.path)
        self.adder.apply_template_and_add(
            repo,
            template,
            data=data,
            out_root=out_root,
            add_mode=add_mode,
            no_input=no_input,
            merged_branch_name=project_config.merged_branch_name,
            template_branch_name=project_config.template_branch_name,
            config_manager=self.config_manager,
            renderer=self.renderer,
            updater=self.updater,
        )

    def update(
        self,
        names: Optional[List[str]] = None,
        no_input: bool = False,
        project_path: Path = Path("."),
    ):
        project_config = self.config_manager.load_project_config(project_path)
        templates: List[Template]
        if names:
            # User wants to update targeted template sources
            templates = [
                self.config_manager.get_template_by_name(
                    name, project_root=project_config.path
                )
                for name in names
            ]
        else:
            # User wants to update all templates
            renderables = self.config_manager.get_renderables(
                project_root=project_config.path
            )
            templates = [renderable.template for renderable in renderables]

        self.updater.update_passed_templates_to_target_versions(
            templates,
            project_root=project_config.path,
            finder=self.finder,
            config_manager=self.config_manager,
        )
        updates = self.updater.get_updates_for_templates(
            templates,
            config_manager=self.config_manager,
            project_root=project_config.path,
        )

        repo = Repo(project_config.path)
        self.updater.update(
            repo,
            updates,
            no_input=no_input,
            merged_branch_name=project_config.merged_branch_name,
            template_branch_name=project_config.template_branch_name,
            renderer=self.renderer,
            config_manager=self.config_manager,
        )

    # TODO: list template sources, list applied templates, remove applied templates and sources
