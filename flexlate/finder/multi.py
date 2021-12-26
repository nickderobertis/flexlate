from typing import Sequence, Optional, List, Final

from flexlate.exc import InvalidTemplatePathException
from flexlate.finder.specific.base import TemplateFinder
from flexlate.finder.specific.cookiecutter import CookiecutterFinder

# TODO: add a way for user to extend specific finders
from flexlate.finder.specific.copier import CopierFinder
from flexlate.template.base import Template
from flexlate.template_path import get_local_repo_path_and_name_cloning_if_repo_url

SPECIFIC_FINDERS: Final[List[TemplateFinder]] = [
    CookiecutterFinder(),
    CopierFinder(),
]


class MultiFinder:
    def find(
        self,
        path: str,
        version: Optional[str] = None,
        finders: Optional[Sequence[TemplateFinder]] = None,
    ) -> Template:
        local_path, name = get_local_repo_path_and_name_cloning_if_repo_url(
            path, version
        )
        finders = finders or SPECIFIC_FINDERS
        for finder in finders:
            if finder.matches_template_type(local_path):
                return finder.find(path, local_path, version=version, name=name)
        raise InvalidTemplatePathException(
            f"could not find a template at {path} with any of the registered template finders"
        )
