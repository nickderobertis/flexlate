import json

import pytest
from git import Repo

from flexlate.config import FlexlateConfig
from flexlate.ext_git import stage_and_commit_all
from flexlate.main import Flexlate
from flexlate.path_ops import change_directory_to
from flexlate.user_config_manager import UserConfigManager
from tests.config import (
    GENERATED_REPO_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_VERSION_1,
    COPIER_REMOTE_NAME,
    COPIER_REMOTE_URL,
    COPIER_REMOTE_VERSION_1,
)
from tests.fixtures.git import *

fxt = Flexlate()


@pytest.fixture
def repo_with_default_flexlate_project(repo_with_placeholder_committed: Repo) -> Repo:
    repo = repo_with_placeholder_committed
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
    yield repo


@pytest.fixture
def repo_with_copier_remote_version_one(
    repo_with_default_flexlate_project: Repo,
) -> Repo:
    repo = repo_with_default_flexlate_project
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.add_template_source(
            COPIER_REMOTE_URL, target_version=COPIER_REMOTE_VERSION_1
        )
        # TODO: Allow updating template sources even when there are no applied templates
        #  It should not be necessary to add this template for the update cli integration tests to pass
        #  Need to rework the process of getting updates, right now it relies on there being applied templates
        fxt.apply_template_and_add(COPIER_REMOTE_NAME, no_input=True)
    yield repo


@pytest.fixture
def repo_with_copier_remote_version_one_and_no_target_version(
    repo_with_copier_remote_version_one: Repo,
) -> Repo:
    repo = repo_with_copier_remote_version_one
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.update_template_source_target_version(
            COPIER_REMOTE_NAME, None, project_path=GENERATED_REPO_DIR
        )
    yield repo


@pytest.fixture
def repo_with_copier_remote_version_one_no_target_version_and_will_have_a_conflict_on_update(
    repo_with_copier_remote_version_one_and_no_target_version: Repo,
) -> Repo:
    repo = repo_with_copier_remote_version_one_and_no_target_version
    # Reformat the flexlate config to cause a conflict
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config_data = json.loads(config_path.read_text())
    config_path.write_text(json.dumps(config_data, indent=4))
    stage_and_commit_all(repo, "Reformat flexlate config to cause a conflict on update")
    yield repo
