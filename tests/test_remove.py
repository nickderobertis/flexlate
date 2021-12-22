import pytest
from git import Repo

from flexlate.config import FlexlateConfig
from flexlate.exc import (
    CannotRemoveTemplateSourceException,
    CannotRemoveAppliedTemplateException,
)
from flexlate.remover import Remover
from tests.config import COOKIECUTTER_ONE_NAME, COOKIECUTTER_TWO_NAME
from tests.fileutils import cookiecutter_one_generated_text_content
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


def test_remove_applied_template(repo_with_template_branch_from_cookiecutter_one: Repo):
    repo = repo_with_template_branch_from_cookiecutter_one
    remover = Remover()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    output_path = GENERATED_REPO_DIR / "b" / "text.txt"
    with change_directory_to(GENERATED_REPO_DIR):
        assert output_path.read_text() == "b"
        remover.remove_applied_template_and_output(repo, COOKIECUTTER_ONE_NAME)

    assert not output_path.exists()
    config = FlexlateConfig.load(config_path)
    assert len(config.template_sources) == 1
    assert len(config.applied_templates) == 0


def test_remove_applied_template_that_does_not_exist(
    repo_with_cookiecutter_one_template_source: Repo,
):
    repo = repo_with_cookiecutter_one_template_source
    remover = Remover()
    with change_directory_to(GENERATED_REPO_DIR):
        with pytest.raises(CannotRemoveAppliedTemplateException) as exc_info:
            remover.remove_applied_template_and_output(repo, COOKIECUTTER_ONE_NAME)
        assert "Cannot find any applied template with name" in str(exc_info.value)
