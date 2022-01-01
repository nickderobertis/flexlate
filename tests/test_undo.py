import pytest

from flexlate.config import FlexlateConfig
from flexlate.exc import (
    LastCommitWasNotByFlexlateException,
    TooFewTransactionsException,
)
from flexlate.transactions.undoer import Undoer
from tests.config import GENERATED_FILES_DIR
from tests.fixtures.templated_repo import *

INITIAL_COMMIT_MESSAGE = "Initial commit\n"
REPO_WITH_COOKIECUTTER_ONE_SOURCE_COMMIT_MESSAGE = 'Added template source one to .\n\n-------------------BEGIN FLEXLATE TRANSACTION-------------------\n{\n  "type": "add source",\n  "target": null,\n  "out_root": null,\n  "data": null,\n  "id": "93f984ca-6e8f-45e9-b9b0-aebebfe798c1"\n}\n'
REPO_WITH_TEMPLATE_BRANCH_FROM_COOKIECUTTER_ONE_COMMIT_MESSAGE = 'Update flexlate templates\n\none: 1c154af24ff30bc4cab8cf9d543304d9\n\n-------------------BEGIN FLEXLATE TRANSACTION-------------------\n{\n  "type": "add output",\n  "target": null,\n  "out_root": null,\n  "data": null,\n  "id": "86465f4d-9752-4ae5-aaa7-791b4c814e8d"\n}\n'


def test_undo_add_template_source(repo_with_cookiecutter_one_template_source: Repo):
    repo = repo_with_cookiecutter_one_template_source
    undoer = Undoer()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    with change_directory_to(GENERATED_REPO_DIR):
        assert config_path.exists()
        assert repo.commit().message == REPO_WITH_COOKIECUTTER_ONE_SOURCE_COMMIT_MESSAGE
        undoer.undo_transactions(repo)
        assert not config_path.exists()
        assert repo.commit().message == INITIAL_COMMIT_MESSAGE


def test_undo_adding_applied_template(
    repo_with_template_branch_from_cookiecutter_one: Repo,
):
    repo = repo_with_template_branch_from_cookiecutter_one
    undoer = Undoer()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    output_path = GENERATED_REPO_DIR / "b" / "text.txt"
    with change_directory_to(GENERATED_REPO_DIR):
        assert output_path.read_text() == "b"
        assert (
            repo.commit().message
            == REPO_WITH_TEMPLATE_BRANCH_FROM_COOKIECUTTER_ONE_COMMIT_MESSAGE
        )
        undoer.undo_transactions(repo)
        assert repo.commit().message == REPO_WITH_COOKIECUTTER_ONE_SOURCE_COMMIT_MESSAGE

    assert not output_path.exists()
    config = FlexlateConfig.load(config_path)
    assert len(config.template_sources) == 1
    assert len(config.applied_templates) == 0


def test_undo_multiple_transactions(
    repo_with_template_branch_from_cookiecutter_one: Repo,
):
    repo = repo_with_template_branch_from_cookiecutter_one
    undoer = Undoer()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    output_path = GENERATED_REPO_DIR / "b" / "text.txt"
    with change_directory_to(GENERATED_REPO_DIR):
        assert output_path.read_text() == "b"
        assert (
            repo.commit().message
            == REPO_WITH_TEMPLATE_BRANCH_FROM_COOKIECUTTER_ONE_COMMIT_MESSAGE
        )
        undoer.undo_transactions(repo, num_transactions=2)
        assert not output_path.exists()
        assert repo.commit().message == INITIAL_COMMIT_MESSAGE

    assert not output_path.exists()
    assert not config_path.exists()


def test_undo_too_many_transactions(repo_with_cookiecutter_one_template_source: Repo):
    repo = repo_with_cookiecutter_one_template_source
    undoer = Undoer()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    with change_directory_to(GENERATED_REPO_DIR):
        assert config_path.exists()
        assert repo.commit().message == REPO_WITH_COOKIECUTTER_ONE_SOURCE_COMMIT_MESSAGE
        with pytest.raises(TooFewTransactionsException):
            undoer.undo_transactions(repo, num_transactions=2)
        assert config_path.exists()
        assert repo.commit().message == REPO_WITH_COOKIECUTTER_ONE_SOURCE_COMMIT_MESSAGE


def test_undo_when_last_commit_is_not_from_flexlate(
    repo_with_placeholder_committed: Repo,
):
    repo = repo_with_placeholder_committed
    undoer = Undoer()
    with change_directory_to(GENERATED_REPO_DIR):
        with pytest.raises(LastCommitWasNotByFlexlateException):
            undoer.undo_transactions(repo)
