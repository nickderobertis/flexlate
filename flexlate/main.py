from pathlib import Path
from typing import Optional, List

from git import Repo

from flexlate.adder import Adder
from flexlate.add_mode import AddMode
from flexlate.config_manager import ConfigManager
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

    def add_template_source(
        self,
        path: str,
        name: Optional[str] = None,
        template_root: Path = Path("."),
        project_path: Path = Path("."),
        add_mode: AddMode = AddMode.LOCAL,
    ):
        project_config = self.config_manager.load_project_config(project_path)
        template = self.finder.find(path)
        if name:
            template.name = name
        self.adder.add_template_source(
            template,
            out_root=template_root,
            add_mode=add_mode,
            config_manager=self.config_manager,
            project_root=project_config.path,
        )

    def apply_template_and_add(
        self,
        name: str,
        data: Optional[TemplateData] = None,
        out_root: Path = Path("."),
        add_mode: AddMode = AddMode.LOCAL,
        no_input: bool = False,
    ):
        project_config = self.config_manager.load_project_config(out_root)
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
            branch_name=project_config.flexlate_branch_name,
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
            templates, _ = self.config_manager.get_templates_with_data(
                project_root=project_config.path
            )

        # TODO: check for updates in templates. Need to ensure we have the original
        #  path in the source, e.g. github url. Will need to implement logic to pull
        #  down VCS or at least compare version. Modify the templates in place here

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
            branch_name=project_config.flexlate_branch_name,
            renderer=self.renderer,
            config_manager=self.config_manager,
        )

    def init_project(
        self,
        path: Path = Path("."),
        default_add_mode: AddMode = AddMode.LOCAL,
        branch_name: str = "flexlate-output",
        user: bool = False,
    ):
        self.config_manager.add_project(
            path=path, default_add_mode=default_add_mode, user=user, branch_name=branch_name
        )
