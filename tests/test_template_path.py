from pathlib import Path

import pytest

from flexlate.exc import InvalidTemplatePathException
from flexlate.template_path import (
    is_repo_url,
    is_local_template,
    get_local_repo_path_cloning_if_repo_url,
)
from tests.config import GENERATED_FILES_DIR
from tests.dirutils import wipe_generated_folder
from tests.fixtures.repo_path import (
    repo_path_fixture,
    repo_path_non_ssh_fixture,
    RepoPathFixture,
)


def test_is_repo_url(repo_path_fixture: RepoPathFixture):
    assert is_repo_url(repo_path_fixture.path) == repo_path_fixture.is_repo_url


def test_is_local_path(repo_path_fixture: RepoPathFixture):
    assert is_local_template(repo_path_fixture.path) == repo_path_fixture.is_local_path


# TODO: figure out how to test cloning SSH urls
def test_get_local_repo_path_cloning_if_repo_url(
    repo_path_non_ssh_fixture: RepoPathFixture,
):
    repo_path_fixture = repo_path_non_ssh_fixture
    wipe_generated_folder()
    if not repo_path_fixture.is_repo_url and not repo_path_fixture.is_local_path:
        # Invalid path test
        with pytest.raises(InvalidTemplatePathException):
            get_local_repo_path_cloning_if_repo_url(
                repo_path_fixture.path, GENERATED_FILES_DIR
            )
        # Path was invalid so nothing else to check, end test
        return

    # Must be valid template path, local or remote
    local_path = get_local_repo_path_cloning_if_repo_url(
        repo_path_fixture.path, GENERATED_FILES_DIR
    )
    if repo_path_fixture.is_local_path:
        assert local_path == Path(repo_path_fixture.path)
    elif repo_path_fixture.is_repo_url:
        assert local_path == GENERATED_FILES_DIR / repo_path_fixture.name
        assert repo_path_fixture.was_cloned_correctly(local_path)
