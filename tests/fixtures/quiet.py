import pytest


@pytest.fixture(scope="module", params=[False, True])
def quiet(request) -> bool:
    return request.param
