from pathlib import Path
from typing import Optional

from flexlate.add_mode import AddMode
from flexlate.config import FlexlateConfig, FlexlateProjectConfig
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.template.base import Template
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.template.types import TemplateType
from tests.config import GENERATED_REPO_DIR


def assert_template_source_cookiecutter_one_added_correctly(
    cookiecutter_one_template: CookiecutterTemplate,
    num_sources: int = 1,
    source_idx: int = 0,
    num_applied_templates: int = 0,
    target_version: Optional[str] = None,
):
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == num_applied_templates
    assert len(config.template_sources) == num_sources
    source = config.template_sources[source_idx]
    assert source.name == cookiecutter_one_template.name
    assert source.path == str(cookiecutter_one_template.path)
    assert source.version == cookiecutter_one_template.version
    assert source.type == TemplateType.COOKIECUTTER
    assert source.target_version == target_version
    assert source.render_relative_root_in_output == Path("{{ cookiecutter.a }}")
    assert source.render_relative_root_in_template == Path("{{ cookiecutter.a }}")


def assert_cookiecutter_one_applied_template_added_correctly(
    template: Template,
    config_dir: Path = GENERATED_REPO_DIR,
    template_root: Path = Path(".."),
    add_mode=AddMode.LOCAL,
):
    config_path = config_dir / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.name == template.name
    assert at.version == template.version
    assert at.data == {"a": "b", "c": ""}
    assert at.root == template_root
    assert at.add_mode == add_mode


def assert_project_config_is_correct(add_mode: AddMode = AddMode.LOCAL):
    projects_config_path = GENERATED_REPO_DIR / "flexlate-project.json"
    projects_config = FlexlateProjectConfig.load(projects_config_path)
    assert len(projects_config.projects) == 1
    project_config = projects_config.projects[0]
    assert project_config.path == Path(".")
    assert project_config.default_add_mode == add_mode
    assert project_config.merged_branch_name == DEFAULT_MERGED_BRANCH_NAME
    assert project_config.template_branch_name == DEFAULT_TEMPLATE_BRANCH_NAME
    assert project_config.remote == "origin"
