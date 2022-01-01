from flexlate.transactions.undoer import Undoer
from tests.fixtures.templated_repo import *


def test_undo_add_template_source(repo_with_cookiecutter_one_template_source: Repo):
    repo = repo_with_cookiecutter_one_template_source
    undoer = Undoer()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    with change_directory_to(GENERATED_REPO_DIR):
        assert config_path.exists()
        undoer.undo_transactions(repo)
        assert not config_path.exists()
        # TODO: check branch history to ensure commits no longer there
