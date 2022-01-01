from flexlate.adder import Adder
from flexlate.transactions.transaction import FlexlateTransaction
from tests.fileutils import preprend_cookiecutter_one_generated_text

from tests.fixtures.git import *
from tests.fixtures.template import *
from tests.fixtures.transaction import add_source_transaction, add_output_transaction


@pytest.fixture
def repo_with_cookiecutter_one_template_source(
    repo_with_placeholder_committed: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_placeholder_committed
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.add_template_source(
            repo,
            cookiecutter_one_template,
            add_source_transaction,
            out_root=GENERATED_REPO_DIR,
        )
    yield repo


@pytest.fixture
def repo_with_gitignore_and_cookiecutter_one_template_source(
    repo_with_gitignore: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_gitignore
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.add_template_source(
            repo,
            cookiecutter_one_template,
            add_source_transaction,
            out_root=GENERATED_REPO_DIR,
        )
    yield repo


@pytest.fixture
def repo_with_remote_cookiecutter_template_source(
    repo_with_placeholder_committed: Repo,
    cookiecutter_remote_template: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_placeholder_committed
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.add_template_source(
            repo,
            cookiecutter_remote_template,
            add_source_transaction,
            out_root=GENERATED_REPO_DIR,
        )
    yield repo


@pytest.fixture
def repo_with_template_branch_from_cookiecutter_one(
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_cookiecutter_one_template_source
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.apply_template_and_add(
            repo,
            cookiecutter_one_template,
            add_output_transaction,
            out_root=GENERATED_REPO_DIR,
            no_input=True,
        )
    yield repo


@pytest.fixture
def repo_with_gitignore_and_template_branch_from_cookiecutter_one(
    repo_with_gitignore_and_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_gitignore_and_cookiecutter_one_template_source
    with change_directory_to(GENERATED_REPO_DIR):
        adder = Adder()
        adder.apply_template_and_add(
            repo,
            cookiecutter_one_template,
            add_output_transaction,
            out_root=GENERATED_REPO_DIR,
            no_input=True,
        )
    yield repo


@pytest.fixture
def repo_from_cookiecutter_one_with_modifications(
    repo_with_template_branch_from_cookiecutter_one: Repo,
) -> Repo:
    repo = repo_with_template_branch_from_cookiecutter_one
    with change_directory_to(GENERATED_REPO_DIR):
        preprend_cookiecutter_one_generated_text("hello\n")
        stage_and_commit_all(repo, "Prepend cookiecutter text with hello")
    yield repo


@pytest.fixture
def repo_with_cookiecutter_one_template_source_and_output(
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
) -> Repo:
    repo = repo_with_cookiecutter_one_template_source
    adder = Adder()
    with change_directory_to(GENERATED_REPO_DIR):
        adder.apply_template_and_add(
            repo, cookiecutter_one_template, add_output_transaction, no_input=True
        )
    yield repo
