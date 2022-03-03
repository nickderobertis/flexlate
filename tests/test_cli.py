from functools import partial

from flexlate.template.copier import CopierTemplate
from tests.fixtures.templated_repo import *
from tests.fixtures.template import *
from tests.fixtures.transaction import *
from tests.integration.cli_stub import fxt as _fxt, ExceptionHandling

# Ignore exceptions so that we can test error codes instead
fxt = partial(_fxt, exception_handling=ExceptionHandling.IGNORE)


def test_check_returns_code_1_when_updates_available(
    repo_with_cookiecutter_remote_version_one_template_source_and_no_target_version: Repo,
    copier_one_template: CopierTemplate,
    add_source_transaction: FlexlateTransaction,
):
    with change_directory_to(GENERATED_REPO_DIR):
        result = fxt("check")
    assert result.exit_code == 1


def test_check_returns_code_0_when_no_updates_available(
    repo_with_cookiecutter_remote_version_one_template_source: Repo,
    copier_one_template: CopierTemplate,
    add_source_transaction: FlexlateTransaction,
):
    with change_directory_to(GENERATED_REPO_DIR):
        result = fxt("check")
    assert result.exit_code == 0
