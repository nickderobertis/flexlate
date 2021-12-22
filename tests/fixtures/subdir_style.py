from enum import Enum
from typing import List, Final

import pytest


class SubdirStyle(str, Enum):
    CD = "cd"
    PROVIDE_RELATIVE = "provide relative"
    PROVIDE_ABSOLUTE = "provide absolute"


all_subdir_styles: Final[List[SubdirStyle]] = list(SubdirStyle)


@pytest.fixture(scope="module", params=all_subdir_styles)
def subdir_style(request) -> SubdirStyle:
    return request.param
