from flexlate.transactions.undoer import Undoer
from tests.fixtures.templated_repo import *

REPO_WITH_COOKIECUTTER_ONE_SOURCE_COMMIT_MESSAGE = 'Added template source one to .\n\n-------------------BEGIN FLEXLATE TRANSACTION-------------------\n{\n  "type": "add source",\n  "target": null,\n  "out_root": null,\n  "data": null,\n  "id": "93f984ca-6e8f-45e9-b9b0-aebebfe798c1"\n}\n'


def test_undo_add_template_source(repo_with_cookiecutter_one_template_source: Repo):
    repo = repo_with_cookiecutter_one_template_source
    undoer = Undoer()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    with change_directory_to(GENERATED_REPO_DIR):
        assert config_path.exists()
        assert repo.commit().message == REPO_WITH_COOKIECUTTER_ONE_SOURCE_COMMIT_MESSAGE
        undoer.undo_transactions(repo)
        assert not config_path.exists()
        assert repo.commit().message == "Initial commit\n"
