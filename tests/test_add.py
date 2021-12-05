from git import Repo, Head

from flexlate.adder import Adder
from flexlate.config import FlexlateConfig, FlexlateProjectConfig
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.template.types import TemplateType
from tests.config import GENERATED_FILES_DIR, GENERATED_REPO_DIR
from tests.fixtures.git import *
from tests.fixtures.template import *
from tests.fixtures.templated_repo import *


def test_add_template_source_to_repo(
    repo_with_placeholder_committed: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
):
    repo = repo_with_placeholder_committed
    adder = Adder()
    adder.add_template_source(
        repo,
        cookiecutter_one_template,
        out_root=GENERATED_REPO_DIR,
        target_version="some version",
    )
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 0
    assert len(config.template_sources) == 1
    source = config.template_sources[0]
    assert source.name == cookiecutter_one_template.name
    assert source.path == str(cookiecutter_one_template.path)
    assert source.version == cookiecutter_one_template.version
    assert source.type == TemplateType.COOKIECUTTER
    assert source.target_version == "some version"


def test_add_local_cookiecutter_applied_template_to_repo(
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
):
    repo = repo_with_cookiecutter_one_template_source
    template = cookiecutter_one_template
    adder = Adder()
    adder.apply_template_and_add(
        repo, template, out_root=GENERATED_REPO_DIR, no_input=True
    )

    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    assert len(config.template_sources) == 1
    at = config.applied_templates[0]
    assert at.name == template.name
    assert at.version == template.version
    assert at.data == {"a": "b", "c": ""}
    assert at.root == GENERATED_REPO_DIR


def test_add_remote_cookiecutter_applied_template_to_repo(
    repo_with_remote_cookiecutter_template_source: Repo,
    cookiecutter_remote_template: CookiecutterTemplate,
):
    repo = repo_with_remote_cookiecutter_template_source
    template = cookiecutter_remote_template
    adder = Adder()
    adder.apply_template_and_add(
        repo, template, out_root=GENERATED_REPO_DIR, no_input=True
    )

    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    assert len(config.template_sources) == 1
    at = config.applied_templates[0]
    assert at.name == template.name
    assert at.version == template.version
    assert at.data == {"name": "abc", "key": "value"}
    assert at.root == GENERATED_REPO_DIR


# TODO: tests for different add modes, different out roots
# TODO: ensure it uses a relative path when it is a project or local config
# TODO: test for adding to existing


def test_add_project_config_with_git(repo_with_placeholder_committed: Repo):
    repo = repo_with_placeholder_committed
    adder = Adder()
    adder.init_project_and_add_to_branches(repo)

    for branch_name in [
        "master",
        DEFAULT_MERGED_BRANCH_NAME,
        DEFAULT_TEMPLATE_BRANCH_NAME,
    ]:
        branch: Head = repo.branches[branch_name]  # type: ignore
        branch.checkout()
        config = FlexlateProjectConfig.load(
            GENERATED_REPO_DIR / "flexlate-project.json"
        )
        assert len(config.projects) == 1
        project = config.projects[0]
        assert project.path == Path(".")
