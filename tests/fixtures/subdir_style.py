from enum import Enum
from typing import List, Final, Optional

import pytest


class SubdirStyle(str, Enum):
    CD = "cd"
    PROVIDE_RELATIVE = "provide relative"
    PROVIDE_ABSOLUTE = "provide absolute"


all_subdir_styles: Final[List[SubdirStyle]] = list(SubdirStyle)
all_subdir_styles_or_none: Final[List[Optional[SubdirStyle]]] = [
    None,
    *all_subdir_styles,
]


@pytest.fixture(scope="module", params=all_subdir_styles)
def subdir_style(request) -> SubdirStyle:
    return request.param


@pytest.fixture(scope="module", params=all_subdir_styles_or_none)
def subdir_style_or_none(request) -> Optional[SubdirStyle]:
    return request.param
