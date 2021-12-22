from git import Repo

from flexlate.config import FlexlateConfig
from flexlate.exc import CannotRemoveTemplateSourceException
from flexlate.remover import Remover
from tests.config import COOKIECUTTER_ONE_NAME, COOKIECUTTER_TWO_NAME
from tests.fixtures.templated_repo import *


def test_remove_template_source(repo_with_cookiecutter_one_template_source: Repo):
    repo = repo_with_cookiecutter_one_template_source
    remover = Remover()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    with change_directory_to(GENERATED_REPO_DIR):
        assert config_path.exists()
        remover.remove_template_source(repo, COOKIECUTTER_ONE_NAME)
        assert not config_path.exists()


def test_remove_template_source_when_multiple_exist(
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_two_template: CookiecutterTemplate,
):
    repo = repo_with_cookiecutter_one_template_source
    remover = Remover()
    adder = Adder()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    with change_directory_to(GENERATED_REPO_DIR):
        adder.add_template_source(repo, cookiecutter_two_template)
        remover.remove_template_source(repo, COOKIECUTTER_ONE_NAME)

    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 0
    assert len(config.template_sources) == 1
    template_source = config.template_sources[0]
    assert template_source.name == COOKIECUTTER_TWO_NAME


def test_remove_non_existing_template_source(repo_with_placeholder_committed: Repo):
    repo = repo_with_placeholder_committed
    remover = Remover()
    with change_directory_to(GENERATED_REPO_DIR):
        with pytest.raises(CannotRemoveTemplateSourceException) as exc_info:
            remover.remove_template_source(repo, COOKIECUTTER_ONE_NAME)
        assert "Cannot find any template source" in str(exc_info.value)


def test_remove_template_source_when_output_exists(
    repo_with_cookiecutter_one_template_source_and_output: Repo,
):
    repo = repo_with_cookiecutter_one_template_source_and_output
    remover = Remover()
    with change_directory_to(GENERATED_REPO_DIR):
        with pytest.raises(CannotRemoveTemplateSourceException) as exc_info:
            remover.remove_template_source(repo, COOKIECUTTER_ONE_NAME)
        assert "has existing outputs" in str(exc_info.value)
