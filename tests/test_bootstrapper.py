from git import Repo

from flexlate.bootstrapper import Bootstrapper
from flexlate.config import FlexlateProjectConfig
from tests.fixtures.templated_repo import *
from tests.fixtures.transaction import bootstrap_transaction
from tests.fs_checks import (
    assert_template_source_cookiecutter_one_added_correctly,
    assert_cookiecutter_one_applied_template_added_correctly,
)


def test_bootstrap_cookiecutter_one(
    repo_with_cookiecutter_one_applied_but_no_flexlate: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    bootstrap_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_applied_but_no_flexlate
    template = cookiecutter_one_template

    bootstrapper = Bootstrapper()
    bootstrapper.bootstrap_flexlate_init_from_existing_template(
        repo, template, bootstrap_transaction, no_input=True, data=dict(a="b", c="")
    )

    # Check that all Flexlate config files are correct
    assert_template_source_cookiecutter_one_added_correctly(cookiecutter_one_template)
    assert_cookiecutter_one_applied_template_added_correctly(
        template, GENERATED_REPO_DIR / "b"
    )
    projects_config_path = GENERATED_REPO_DIR / "flexlate-project.json"
    projects_config = FlexlateProjectConfig.load(projects_config_path)
    assert len(projects_config.projects) == 1
    project_config = projects_config.projects[0]
    assert project_config.path == Path(".")
    assert project_config.default_add_mode == AddMode.LOCAL
    assert project_config.merged_branch_name == DEFAULT_MERGED_BRANCH_NAME
    assert project_config.template_branch_name == DEFAULT_TEMPLATE_BRANCH_NAME
    assert project_config.remote == "origin"

    # Check to make sure flexlate merged branch exists and is up to date
    master = repo.active_branch
    merged_branch = repo.branches[DEFAULT_MERGED_BRANCH_NAME]  # type: ignore
    assert merged_branch.commit.hexsha == master.commit.hexsha
