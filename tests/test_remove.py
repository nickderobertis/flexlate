from git import Repo

from flexlate.config import FlexlateConfig
from flexlate.remover import Remover
from tests.config import COOKIECUTTER_REMOTE_NAME
from tests.fixtures.templated_repo import *


def test_remove_template_source(repo_with_remote_cookiecutter_template_source: Repo):
    repo = repo_with_remote_cookiecutter_template_source
    remover = Remover()
    with change_directory_to(GENERATED_REPO_DIR):
        remover.remove_template_source(repo, COOKIECUTTER_REMOTE_NAME)
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 0
    assert len(config.template_sources) == 0
