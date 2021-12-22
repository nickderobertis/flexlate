from typing import List, Final

import pytest

from flexlate.add_mode import AddMode

all_add_modes: Final[List[AddMode]] = list(AddMode)


@pytest.fixture(scope="module", params=all_add_modes)
def add_mode(request) -> AddMode:
    return request.param
