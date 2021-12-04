from typing import Sequence, Optional

from flexlate.exc import InvalidTemplatePathException
from flexlate.finder.specific.base import TemplateFinder
from flexlate.finder.specific.cookiecutter import CookiecutterFinder

# TODO: add a way for user to extend specific finders
from flexlate.template.base import Template

SPECIFIC_FINDERS = [
    CookiecutterFinder(),
]

# TODO: move downloading of vcs projects into multi finder, so they don't
#  each have to pull them down while checking if they match the finder


class MultiFinder:
    def find(
        self,
        path: str,
        version: Optional[str] = None,
        finders: Optional[Sequence[TemplateFinder]] = None,
    ) -> Template:
        finders = finders or SPECIFIC_FINDERS
        for finder in finders:
            if finder.matches_template_type(path):
                return finder.find(path, version=version)
        raise InvalidTemplatePathException(
            f"could not find a template at {path} with any of the registered template finders"
        )
