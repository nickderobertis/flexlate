import shutil
from typing import Optional
from unittest.mock import patch

import appdirs

from flexlate.user_config_manager import UserConfigManager
from tests.config import GENERATED_FILES_DIR
from tests.fixtures.add_mode import *
from tests.fixtures.templated_repo import *
from tests.fixtures.transaction import update_target_version_transaction
from tests.gitutils import assert_main_commit_message_matches


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_add_local_cookiecutter_applied_template_to_repo(
    add_mode: AddMode,
    repo_with_cookiecutter_one_template_source: Repo,
    update_target_version_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    transaction = update_target_version_transaction

    manager = UserConfigManager()

    if add_mode == AddMode.USER:
        # Template source was already added at project root before this, so need to move config
        shutil.move(str(GENERATED_REPO_DIR / "flexlate.json"), str(GENERATED_FILES_DIR))
        config_dir = GENERATED_FILES_DIR
    elif add_mode in (AddMode.PROJECT, AddMode.LOCAL):
        config_dir = GENERATED_REPO_DIR
    else:
        raise NotImplementedError(f"unsupported add mode {add_mode}")

    config_path = config_dir / "flexlate.json"

    def assert_target_version_is(version: Optional[str]):
        config = FlexlateConfig.load(config_path)
        assert len(config.template_sources) == 1
        ts = config.template_sources[0]
        assert ts.target_version == version

    assert_target_version_is(None)
    target_version = COOKIECUTTER_ONE_VERSION
    manager.update_template_source_target_version(
        COOKIECUTTER_ONE_NAME,
        target_version,
        repo,
        transaction,
        project_path=GENERATED_REPO_DIR,
        add_mode=add_mode,
    )
    assert_target_version_is(target_version)

    if add_mode == AddMode.USER:
        # Should be no changes to git
        last_commit_message = "Added template source one to ."
    elif add_mode in (AddMode.PROJECT, AddMode.LOCAL):
        last_commit_message = (
            f"Changed target version for template source one to {target_version}"
        )
    else:
        raise NotImplementedError(f"unsupported add mode {add_mode}")

    assert_main_commit_message_matches(repo.commit().message, last_commit_message)
