# Integration tests
import os
from pathlib import Path
from unittest.mock import patch

import appdirs

from flexlate.add_mode import AddMode
from flexlate.config import FlexlateConfig, FlexlateProjectConfig
from flexlate.main import Flexlate
from tests.config import (
    GENERATED_FILES_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_NAME,
    COOKIECUTTER_REMOTE_VERSION_2,
    GENERATED_REPO_DIR,
)
from tests.dirutils import change_directory_to
from tests.fixtures.git import *


def test_init_project_and_add_source_and_template(
    repo_with_placeholder_committed: Repo,
):
    repo = repo_with_placeholder_committed
    fxt = Flexlate()
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)

    _assert_project_files_are_correct()
    _assert_config_is_correct()

    project_config_path = GENERATED_REPO_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(project_config_path, user=False)


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_init_project_for_user_and_add_source_and_template(
    repo_with_placeholder_committed: Repo,
):
    repo = repo_with_placeholder_committed
    fxt = Flexlate()
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project(user=True)
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)
    _assert_project_files_are_correct()
    _assert_config_is_correct()

    project_config_path = GENERATED_FILES_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(project_config_path, user=True)


def _assert_project_files_are_correct():
    out_path = GENERATED_REPO_DIR / "abc" / "abc.txt"
    assert out_path.exists()
    content = out_path.read_text()
    assert content == "some new header\nvalue"


def _assert_config_is_correct():
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    # Template source
    assert len(config.template_sources) == 1
    template_source = config.template_sources[0]
    assert template_source.name == COOKIECUTTER_REMOTE_NAME
    assert template_source.version == COOKIECUTTER_REMOTE_VERSION_2
    assert template_source.git_url == COOKIECUTTER_REMOTE_URL
    # Applied template
    assert len(config.applied_templates) == 1
    applied_template = config.applied_templates[0]
    assert applied_template.name == COOKIECUTTER_REMOTE_NAME
    assert applied_template.data == {"name": "abc", "key": "value"}
    assert applied_template.version == COOKIECUTTER_REMOTE_VERSION_2
    assert applied_template.root == Path(".")


def _assert_project_config_is_correct(path: Path, user: bool = False):
    project_config = FlexlateProjectConfig.load(path)
    assert len(project_config.projects) == 1
    project = project_config.projects[0]
    if user:
        assert project.path == project.path.absolute()
        assert project.path == GENERATED_REPO_DIR
    else:
        assert project.path != project.path.absolute()
        assert (path.parent / project.path).absolute() == GENERATED_REPO_DIR
    assert project.default_add_mode == AddMode.LOCAL
