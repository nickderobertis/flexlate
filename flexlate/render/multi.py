from pathlib import Path
from typing import Sequence, Optional

from flexlate.exc import InvalidTemplateClassException, RendererNotFoundException
from flexlate.render.specific.base import SpecificTemplateRenderer
from flexlate.render.specific.cookiecutter import CookiecutterRenderer
from flexlate.template.base import Template
from flexlate.template.types import TemplateType
from flexlate.types import TemplateData

renderers = [CookiecutterRenderer()]


class MultiRenderer:

    # TODO: register method to add user-defined template types

    def render(
        self,
        templates: Sequence[Template],
        data: Optional[TemplateData] = None,
        out_path: Path = Path("."),
    ):
        for template in templates:
            renderer = _get_specific_renderer(template)
            # TODO: keep in isolated folders then combine
            renderer.render(template, data=data, out_path=out_path)


def _get_specific_renderer(template: Template) -> SpecificTemplateRenderer:
    if template._type == TemplateType.BASE:
        raise InvalidTemplateClassException(
            f"No renderer for template type base, did you remember to override _type when defining the template type? {template}"
        )
    for renderer in renderers:
        if renderer._template_type == template._type:
            return renderer
    raise RendererNotFoundException(f"No registered renderer for template {template}")
