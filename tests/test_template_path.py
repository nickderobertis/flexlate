import pytest

from flexlate.template_path import is_repo_url, is_local_template
from tests.fixtures.repo_path import repo_path_fixture, RepoPathFixture


def test_is_repo_url(repo_path_fixture: RepoPathFixture):
    assert is_repo_url(repo_path_fixture.path) == repo_path_fixture.is_repo_url


def test_is_local_path(repo_path_fixture: RepoPathFixture):
    assert is_local_template(repo_path_fixture.path) == repo_path_fixture.is_local_path
