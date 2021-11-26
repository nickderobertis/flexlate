import json
from pathlib import Path
from typing import Union

from cookiecutter.config import get_user_config
from cookiecutter.repository import determine_repo_dir

from flexlate.finder.base import TemplateFinder
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.template_config.cookiecutter import CookiecutterConfig


class CookiecutterFinder(TemplateFinder):
    def find(self, path: Union[str, Path]) -> CookiecutterTemplate:
        config_dict = get_user_config()
        repo_dir, _ = determine_repo_dir(
            template=str(path),
            abbreviations=config_dict["abbreviations"],
            clone_to_dir=config_dict["cookiecutters_dir"],
            checkout=None,
            no_input=True,
        )
        repo_path = Path(repo_dir)
        config = self.get_config(repo_path)
        return CookiecutterTemplate(config, repo_path)

    def get_config(self, directory: Path) -> CookiecutterConfig:
        config_path = directory / "cookiecutter.json"
        data = json.loads(config_path.read_text())
        return CookiecutterConfig(data)
