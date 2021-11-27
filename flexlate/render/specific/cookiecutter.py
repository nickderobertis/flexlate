from pathlib import Path
from typing import Optional

from cookiecutter.main import cookiecutter

from flexlate.render.specific.base import SpecificTemplateRenderer
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.template.types import TemplateType
from flexlate.types import TemplateData


class CookiecutterRenderer(SpecificTemplateRenderer):
    _template_cls = CookiecutterTemplate
    _template_type = TemplateType.COOKIECUTTER

    def render(
        self,
        template: CookiecutterTemplate,
        data: Optional[TemplateData] = None,
        out_path: Path = Path("."),
    ):
        cookiecutter(
            str(template.path),
            no_input=True,
            output_dir=str(out_path),
            extra_context=data,
        )
