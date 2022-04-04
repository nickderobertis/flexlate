from enum import Enum
from typing import List, Final

import pytest
from git import Repo

from flexlate.ext_git import delete_local_branch
from tests.gitutils import reset_n_commits_without_checkout


class LocalBranchSituation(str, Enum):
    UP_TO_DATE = "up to date"
    DELETED = "deleted"
    OUT_OF_DATE = "out of date"

    def apply(self, repo: Repo, branch_name: str):
        apply_local_branch_situation(repo, branch_name, self)


all_local_branch_situations: Final[List[LocalBranchSituation]] = list(
    LocalBranchSituation
)


@pytest.fixture(scope="module", params=all_local_branch_situations)
def local_branch_situation(request) -> LocalBranchSituation:
    return request.param


# TODO: see if there is a better way to structure multiple parameterized fixtures
#  that actually resolve to the same value
@pytest.fixture(scope="module", params=all_local_branch_situations)
def template_branch_situation(request) -> LocalBranchSituation:
    return request.param


@pytest.fixture(scope="module", params=all_local_branch_situations)
def output_branch_situation(request) -> LocalBranchSituation:
    return request.param


def apply_local_branch_situation(
    repo: Repo, branch_name: str, situation: LocalBranchSituation
):
    if situation == LocalBranchSituation.UP_TO_DATE:
        return
    if situation == LocalBranchSituation.DELETED:
        return delete_local_branch(repo, branch_name)
    if situation == LocalBranchSituation.OUT_OF_DATE:
        return reset_n_commits_without_checkout(repo, branch_name)
    raise NotImplementedError(f"no handling for local branch situation {situation}")
