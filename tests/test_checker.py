from typing import Optional

import pytest
from git import Repo

from flexlate.checker import Checker
from flexlate.config import FlexlateConfig
from flexlate.exc import TemplateNotRegisteredException
from flexlate.template.copier import CopierTemplate
from tests.config import COOKIECUTTER_REMOTE_NAME, COPIER_ONE_NAME
from tests.fixtures.templated_repo import *
from tests.fixtures.template import *
from tests.fixtures.transaction import *


@pytest.mark.parametrize("names", [None, [COOKIECUTTER_REMOTE_NAME], [COPIER_ONE_NAME]])
def test_check_for_remote_template_update(
    names: Optional[List[str]],
    repo_with_cookiecutter_remote_version_one_template_source_and_no_target_version: Repo,
    copier_one_template: CopierTemplate,
    add_source_transaction: FlexlateTransaction,
):
    repo = (
        repo_with_cookiecutter_remote_version_one_template_source_and_no_target_version
    )
    template = copier_one_template
    checker = Checker()
    adder = Adder()

    # Add a source that is already up to date
    adder.add_template_source(
        repo, template, add_source_transaction, out_root=GENERATED_REPO_DIR
    )

    new_versions = checker.find_new_versions_for_template_sources(
        names=names, project_root=GENERATED_REPO_DIR
    ).update_version_dict
    if names is None or names == [COOKIECUTTER_REMOTE_NAME]:
        assert new_versions == {COOKIECUTTER_REMOTE_NAME: COOKIECUTTER_REMOTE_VERSION_2}
    else:
        assert new_versions == {}


def test_check_for_update_with_no_template_sources(
    repo_with_placeholder_committed: Repo,
):
    checker = Checker()
    new_versions = checker.find_new_versions_for_template_sources(
        project_root=GENERATED_REPO_DIR
    ).update_version_dict
    assert new_versions == {}


def test_check_for_update_template_that_does_not_exist(
    repo_with_placeholder_committed: Repo,
):
    checker = Checker()
    with pytest.raises(TemplateNotRegisteredException):
        checker.find_new_versions_for_template_sources(
            names=["some-fake-template"], project_root=GENERATED_REPO_DIR
        )
