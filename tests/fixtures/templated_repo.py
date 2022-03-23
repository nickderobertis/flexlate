import json
import os

import pytest

from flexlate.add_mode import AddMode
from flexlate.adder import Adder
from flexlate.branch_update import get_flexlate_branch_name
from flexlate.config import FlexlateConfig
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.ext_git import delete_local_branch
from flexlate.remover import Remover
from flexlate.transactions.transaction import FlexlateTransaction
from flexlate.update.main import Updater
from tests.config import COOKIECUTTER_ONE_NAME
from tests.fileutils import preprend_cookiecutter_one_generated_text

from tests.fixtures.git import *
from tests.fixtures.template import *
from tests.fixtures.transaction import (
    add_source_transaction,
    add_output_transaction,
    remove_source_transaction,
    remove_output_transaction,
    update_transaction,
)
from tests.gitutils import rename_branch


@pytest.fixture
def repo_with_cookiecutter_one_template_source(
    repo_with_placeholder_committed: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_placeholder_committed
    template = cookiecutter_one_template

    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.add_template_source(
            repo,
            template,
            add_source_transaction,
            out_root=GENERATED_REPO_DIR,
        )
    yield repo


@pytest.fixture
def repo_with_cookiecutter_remote_version_one_template_source(
    repo_with_placeholder_committed: Repo,
    cookiecutter_remote_version_one_template: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_placeholder_committed
    template = cookiecutter_remote_version_one_template

    adder = Adder()
    adder.add_template_source(
        repo,
        template,
        add_source_transaction,
        out_root=GENERATED_REPO_DIR,
        target_version=COOKIECUTTER_REMOTE_VERSION_1,
    )
    yield repo


@pytest.fixture
def repo_with_cookiecutter_remote_version_one_template_source_and_no_target_version(
    repo_with_cookiecutter_remote_version_one_template_source: Repo,
) -> Repo:
    repo = repo_with_cookiecutter_remote_version_one_template_source

    # Remove target version, allowing the remote version to update
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    ts = config.template_sources[0]
    ts.target_version = None
    config.save()
    stage_and_commit_all(repo, "Remove target version")

    yield repo


@pytest.fixture
def repo_with_cookiecutter_remote_version_one_template_source_that_will_have_merge_conflict_on_flexlate_operation(
    repo_with_cookiecutter_remote_version_one_template_source: Repo,
) -> Repo:
    repo = repo_with_cookiecutter_remote_version_one_template_source

    # Force a merge conflict by reformatting flexlate config
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config_path.write_text(json.dumps(json.loads(config_path.read_text()), indent=4))
    stage_and_commit_all(repo, "Reformat flexlate config")

    yield repo


@pytest.fixture
def repo_with_cookiecutter_remote_version_one_template_source_and_output_that_will_have_merge_conflict_on_flexlate_operation(
    repo_with_template_branch_from_cookiecutter_remote: Repo,
) -> Repo:
    repo = repo_with_template_branch_from_cookiecutter_remote

    # Force a merge conflict by reformatting flexlate config
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config_path.write_text(json.dumps(json.loads(config_path.read_text()), indent=4))
    stage_and_commit_all(repo, "Reformat flexlate config")

    yield repo


@pytest.fixture
def repo_with_copier_output_subdir_template_source(
    repo_with_placeholder_committed: Repo,
    copier_output_subdir_template: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_placeholder_committed
    template = copier_output_subdir_template

    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.add_template_source(
            repo,
            template,
            add_source_transaction,
            out_root=GENERATED_REPO_DIR,
        )
    yield repo


@pytest.fixture
def repo_with_gitignore_and_cookiecutter_one_template_source(
    repo_with_gitignore: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_gitignore
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.add_template_source(
            repo,
            cookiecutter_one_template,
            add_source_transaction,
            out_root=GENERATED_REPO_DIR,
        )
    yield repo


@pytest.fixture
def repo_with_gitignore_and_cookiecutter_one_template_source_in_repo(
    repo_with_gitignore: Repo,
    cookiecutter_one_template_in_repo: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_gitignore
    # While the same changes are in cookiecutter_one_template_in_repo, they do not persist,
    # so make them again
    new_folder = GENERATED_REPO_DIR / "templates"
    new_folder.mkdir(parents=True)
    new_path = new_folder / COOKIECUTTER_ONE_DIR.name
    shutil.copytree(COOKIECUTTER_ONE_DIR, new_path)
    stage_and_commit_all(repo, "Add cookiecutter one template in repo")
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.add_template_source(
            repo,
            cookiecutter_one_template_in_repo,
            add_source_transaction,
            out_root=GENERATED_REPO_DIR,
        )
    yield repo


@pytest.fixture
def repo_with_remote_cookiecutter_template_source(
    repo_with_placeholder_committed: Repo,
    cookiecutter_remote_template: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_placeholder_committed
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.add_template_source(
            repo,
            cookiecutter_remote_template,
            add_source_transaction,
            out_root=GENERATED_REPO_DIR,
        )
    yield repo


@pytest.fixture
def repo_with_template_branch_from_cookiecutter_one(
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_cookiecutter_one_template_source
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.apply_template_and_add(
            repo,
            cookiecutter_one_template,
            add_output_transaction,
            out_root=GENERATED_REPO_DIR,
            no_input=True,
        )
    yield repo


@pytest.fixture
def repo_with_template_branch_from_cookiecutter_remote(
    repo_with_cookiecutter_remote_version_one_template_source: Repo,
    cookiecutter_remote_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_cookiecutter_remote_version_one_template_source
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.apply_template_and_add(
            repo,
            cookiecutter_remote_template,
            add_output_transaction,
            out_root=GENERATED_REPO_DIR,
            add_mode=AddMode.PROJECT,
            no_input=True,
        )
    yield repo


@pytest.fixture
def repo_with_template_branch_from_cookiecutter_one_and_feature_flexlate_branches(
    repo_with_template_branch_from_cookiecutter_one: Repo,
) -> Repo:
    repo = repo_with_template_branch_from_cookiecutter_one
    # Simulate conditions of developing on feature branch
    feature_merged_branch_name = get_flexlate_branch_name(
        repo, DEFAULT_MERGED_BRANCH_NAME
    )
    feature_template_branch_name = get_flexlate_branch_name(
        repo, DEFAULT_TEMPLATE_BRANCH_NAME
    )
    rename_branch(repo, DEFAULT_MERGED_BRANCH_NAME, feature_merged_branch_name)
    rename_branch(repo, DEFAULT_TEMPLATE_BRANCH_NAME, feature_template_branch_name)
    yield repo


@pytest.fixture
def repo_with_template_branch_from_cookiecutter_one_project_add_mode(
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_cookiecutter_one_template_source
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.apply_template_and_add(
            repo,
            cookiecutter_one_template,
            add_output_transaction,
            out_root=GENERATED_REPO_DIR,
            no_input=True,
            add_mode=AddMode.PROJECT,
        )
    yield repo


@pytest.fixture
def repo_with_template_branch_from_cookiecutter_remote_version_one(
    repo_with_cookiecutter_remote_version_one_template_source: Repo,
    cookiecutter_remote_version_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_cookiecutter_remote_version_one_template_source
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.apply_template_and_add(
            repo,
            cookiecutter_remote_version_one_template,
            add_output_transaction,
            out_root=GENERATED_REPO_DIR,
            no_input=True,
            add_mode=AddMode.PROJECT,
        )
    yield repo


@pytest.fixture
def repo_with_gitignore_and_template_branch_from_cookiecutter_one(
    repo_with_gitignore_and_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_gitignore_and_cookiecutter_one_template_source
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.apply_template_and_add(
            repo,
            cookiecutter_one_template,
            add_output_transaction,
            out_root=GENERATED_REPO_DIR,
            no_input=True,
        )
    yield repo


@pytest.fixture
def repo_with_gitignore_and_template_branch_from_cookiecutter_one_in_repo(
    repo_with_gitignore_and_cookiecutter_one_template_source_in_repo: Repo,
    cookiecutter_one_template_in_repo: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_gitignore_and_cookiecutter_one_template_source_in_repo
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.apply_template_and_add(
            repo,
            cookiecutter_one_template_in_repo,
            add_output_transaction,
            out_root=GENERATED_REPO_DIR,
            no_input=True,
        )
    yield repo


@pytest.fixture
def repo_from_cookiecutter_one_with_modifications(
    repo_with_template_branch_from_cookiecutter_one: Repo,
) -> Repo:
    repo = repo_with_template_branch_from_cookiecutter_one
    with change_directory_to(GENERATED_REPO_DIR):
        preprend_cookiecutter_one_generated_text("hello\n")
        stage_and_commit_all(repo, "Prepend cookiecutter text with hello")
    yield repo


@pytest.fixture
def repo_after_updating_cookiecutter_one(
    cookiecutter_one_modified_template: CookiecutterTemplate,
    repo_with_gitignore_and_template_branch_from_cookiecutter_one: Repo,
    update_transaction: FlexlateTransaction,
):
    repo = repo_with_gitignore_and_template_branch_from_cookiecutter_one
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_REPO_DIR
    )
    updater.update(repo, template_updates, update_transaction, no_input=True)
    yield repo


@pytest.fixture
def repo_with_cookiecutter_one_template_source_and_output(
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_cookiecutter_one_template_source
    adder = Adder()
    with change_directory_to(GENERATED_REPO_DIR):
        adder.apply_template_and_add(
            repo, cookiecutter_one_template, add_output_transaction, no_input=True
        )
    yield repo


@pytest.fixture
def repo_with_template_source_removed(
    repo_with_cookiecutter_one_template_source: Repo,
    remove_source_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    remover = Remover()
    with change_directory_to(GENERATED_REPO_DIR):
        remover.remove_template_source(
            repo, COOKIECUTTER_ONE_NAME, remove_source_transaction
        )
    yield repo


@pytest.fixture
def repo_with_applied_output_removed(
    repo_with_template_branch_from_cookiecutter_one: Repo,
    remove_output_transaction: FlexlateTransaction,
):
    repo = repo_with_template_branch_from_cookiecutter_one
    remover = Remover()
    with change_directory_to(GENERATED_REPO_DIR):
        remover.remove_applied_template_and_output(
            repo, COOKIECUTTER_ONE_NAME, remove_output_transaction
        )
    yield repo


@pytest.fixture
def repo_with_cookiecutter_one_applied_but_no_flexlate(
    repo_with_template_branch_from_cookiecutter_one: Repo,
) -> Repo:
    repo = repo_with_template_branch_from_cookiecutter_one
    ts_config_path = GENERATED_REPO_DIR / "flexlate.json"
    os.remove(ts_config_path)
    at_config_path = GENERATED_REPO_DIR / "b" / "flexlate.json"
    os.remove(at_config_path)
    delete_local_branch(repo, DEFAULT_MERGED_BRANCH_NAME)
    delete_local_branch(repo, DEFAULT_TEMPLATE_BRANCH_NAME)
    stage_and_commit_all(
        repo, "Remove flexlate files, converting this into only a cookiecutter template"
    )
    yield repo
