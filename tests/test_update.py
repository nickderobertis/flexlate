from git import Repo, Head

from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.update.ext_git import DEFAULT_BRANCH_NAME
from flexlate.update.main import Updater
from tests.config import GENERATED_FILES_DIR
from tests.fileutils import cookiecutter_one_generated_text_content
from tests.fixtures.git import *
from tests.fixtures.template import cookiecutter_one_template


def test_update_template_no_history(
    cookiecutter_one_template: CookiecutterTemplate,
    repo_with_placeholder_committed: Repo,
):
    repo = repo_with_placeholder_committed
    updater = Updater()
    updater.update(repo, [cookiecutter_one_template])
    main_branch: Head = repo.branches["master"]  # type: ignore
    template_branch: Head = repo.branches[DEFAULT_BRANCH_NAME]  # type: ignore
    assert repo.active_branch == main_branch
    assert cookiecutter_one_generated_text_content() == ""
    template_branch.checkout()
    assert repo.active_branch == template_branch
    assert cookiecutter_one_generated_text_content() == ""


# TODO: test for unclean git directory
# TODO: test for template branch already exists
