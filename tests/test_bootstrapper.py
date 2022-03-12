from git import Repo

from flexlate.bootstrapper import Bootstrapper
from tests.fixtures.templated_repo import *
from tests.fixtures.transaction import bootstrap_transaction


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

    assert True
