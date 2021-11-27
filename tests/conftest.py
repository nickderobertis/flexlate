import pytest

from tests.dirutils import wipe_generated_folder


@pytest.fixture(scope="session", autouse=True)
def after_all():
    yield
    wipe_generated_folder()
