from flexlate.config import FlexlateConfig
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.syncer import Syncer
from tests.fixtures.templated_repo import *
from tests.fixtures.transaction import sync_transaction


def test_sync_change_in_template_source_name(
    repo_with_cookiecutter_one_template_source: Repo,
    sync_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    expect_name = "new-name"

    # Make a manual change in the template source name
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    config.template_sources[0].name = expect_name
    config.save()
    stage_and_commit_all(repo, "Manual change to cookiecutter one name")

    # Sync changes to flexlate branches
    syncer = Syncer()
    syncer.sync_local_changes_to_flexlate_branches(
        repo, sync_transaction, no_input=True
    )

    for branch_name in [
        "master",
        DEFAULT_MERGED_BRANCH_NAME,
        DEFAULT_TEMPLATE_BRANCH_NAME,
    ]:
        branch: Head = repo.branches[branch_name]  # type: ignore
        branch.checkout()
        config = FlexlateConfig.load(config_path)
        assert config.template_sources[0].name == expect_name
