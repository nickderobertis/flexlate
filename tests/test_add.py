from git import Repo

from flexlate.adder import Adder
from flexlate.config import FlexlateConfig
from flexlate.template.types import TemplateType
from tests.config import GENERATED_FILES_DIR
from tests.fixtures.git import *
from tests.fixtures.template import *
from tests.fixtures.templated_repo import *


def test_add_template_source_to_empty_repo(
    empty_generated_repo: Repo, cookiecutter_one_template: CookiecutterTemplate
):
    adder = Adder()
    adder.add_template_source(
        cookiecutter_one_template,
        out_root=GENERATED_FILES_DIR,
        project_root=GENERATED_FILES_DIR,
    )
    config_path = GENERATED_FILES_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 0
    assert len(config.template_sources) == 1
    source = config.template_sources[0]
    assert source.name == cookiecutter_one_template.name
    assert source.path == str(cookiecutter_one_template.path)
    assert source.version == cookiecutter_one_template.version
    assert source.type == TemplateType.COOKIECUTTER


def test_add_applied_template_to_repo(
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
):
    repo = repo_with_cookiecutter_one_template_source
    adder = Adder()
    adder.apply_template_and_add(
        repo, cookiecutter_one_template, out_root=GENERATED_FILES_DIR, no_input=True
    )

    config_path = GENERATED_FILES_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    assert len(config.template_sources) == 1
    at = config.applied_templates[0]
    assert at.name == cookiecutter_one_template.name
    assert at.version == cookiecutter_one_template.version
    assert at.data == {"a": "b", "c": ""}
    assert at.root == GENERATED_FILES_DIR


# TODO: tests for different add modes, different out roots
# TODO: ensure it uses a relative path when it is a project or local config
