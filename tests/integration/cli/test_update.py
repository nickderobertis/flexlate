from git import Repo

from flexlate.path_ops import change_directory_to
from tests.config import GENERATED_REPO_DIR
from tests.integration.fixtures.repo import *
from tests.integration.cli.fxt import fxt


def test_update_returns_code_0_for_update_without_conflict(
    repo_with_copier_remote_version_one_and_no_target_version: Repo,
):
    with change_directory_to(GENERATED_REPO_DIR):
        result = fxt(["update", "--no-input", "--abort"])
    assert result.exit_code == 0


def test_update_returns_code_1_for_template_conflict_with_abort(
    repo_with_copier_remote_version_one_no_target_version_and_will_have_a_conflict_on_update: Repo,
):
    with change_directory_to(GENERATED_REPO_DIR):
        result = fxt(["update", "--no-input", "--abort"])
    assert result.exit_code == 1
