# Integration tests
import os
from pathlib import Path

from flexlate.config import FlexlateConfig
from flexlate.main import Flexlate
from tests.config import GENERATED_FILES_DIR, COOKIECUTTER_REMOTE_URL, COOKIECUTTER_REMOTE_NAME, \
    COOKIECUTTER_REMOTE_VERSION_2
from tests.dirutils import change_directory_to
from tests.fixtures.git import *


def test_init_project_and_add_source_and_template(repo_with_placeholder_committed: Repo):
    repo = repo_with_placeholder_committed
    fxt = Flexlate()
    with change_directory_to(GENERATED_FILES_DIR):
        fxt.init_project()
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)

    # Check content
    out_path = GENERATED_FILES_DIR / "abc" / "abc.txt"
    assert out_path.exists()
    content = out_path.read_text()
    assert content == "some new header\nvalue"

    # Check config
    config_path = GENERATED_FILES_DIR / "flexlate.json"
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
