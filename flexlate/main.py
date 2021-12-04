from pathlib import Path
from typing import Optional, List

from git import Repo

from flexlate.adder import Adder
from flexlate.add_mode import AddMode
from flexlate.config_manager import ConfigManager
from flexlate.finder.multi import MultiFinder

# TODO: determine how to automatically set project root
#  maybe just adding is_project_root into config and some kind of project initialization
#  but need to make sure it will work well with user usage. Then maybe config lists project roots?

# TODO: determine how to set a default for add mode per project
#  maybe just adding to project root config

# TODO: branch name should be in the project config
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

    # TODO: add project init function, sets up project config

    def add_template_source(
        self,
        path: str,
        name: Optional[str] = None,
        template_root: Path = Path("."),
        add_mode: AddMode = AddMode.LOCAL,
    ):
        template = self.finder.find(path)
        if name:
            template.name = name
        # TODO: determine and pass project root
        self.adder.add_template_source(
            template,
            out_root=template_root,
            add_mode=add_mode,
            config_manager=self.config_manager,
        )

    def apply_template_and_add(
        self,
        name: str,
        data: Optional[TemplateData] = None,
        out_root: Path = Path("."),
        add_mode: AddMode = AddMode.LOCAL,
        no_input: bool = False,
    ):
        # TODO: pass project root
        template = self.config_manager.get_template_by_name(name)
        # TODO: get branch name from project config
        # TODO: determine project path, create repo from it
        repo = Repo()
        self.adder.apply_template_and_add(
            repo,
            template,
            data=data,
            out_root=out_root,
            add_mode=add_mode,
            no_input=no_input,
            config_manager=self.config_manager,
            renderer=self.renderer,
            updater=self.updater,
        )

    def update(self, names: Optional[List[str]] = None, no_input: bool = False):
        templates: List[Template]
        if names:
            # User wants to update targeted template sources
            # TODO: pass project root
            templates = [
                self.config_manager.get_template_by_name(name) for name in names
            ]
        else:
            # User wants to update all templates
            # TODO: pass project root
            templates, _ = self.config_manager.get_templates_with_data()

        # TODO: check for updates in templates. Need to ensure we have the original
        #  path in the source, e.g. github url. Will need to implement logic to pull
        #  down VCS or at least compare version. Modify the templates in place here

        # TODO: pass project root
        updates = self.updater.get_updates_for_templates(
            templates, config_manager=self.config_manager
        )

        # TODO: determine project path, create repo from it
        repo = Repo()
        # TODO: get branch name from project config
        self.updater.update(
            repo,
            updates,
            no_input=no_input,
            renderer=self.renderer,
            config_manager=self.config_manager,
        )

    def init_project(
        self,
        path: Path = Path("."),
        default_add_mode: AddMode = AddMode.LOCAL,
        user: bool = False,
    ):
        self.config_manager.add_project(
            path=path, default_add_mode=default_add_mode, user=user
        )
