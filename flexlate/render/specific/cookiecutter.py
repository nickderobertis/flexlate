from pathlib import Path
from typing import Optional

from cookiecutter.config import get_user_config
from cookiecutter.generate import generate_context, generate_files
from cookiecutter.main import cookiecutter
from cookiecutter.prompt import prompt_for_config

from flexlate.render.renderable import Renderable
from flexlate.render.specific.base import SpecificTemplateRenderer
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData


class CookiecutterRenderer(SpecificTemplateRenderer[CookiecutterTemplate]):
    _template_cls = CookiecutterTemplate
    _template_type = TemplateType.COOKIECUTTER

    def render(
        self,
        renderable: Renderable[CookiecutterTemplate],
        no_input: bool = False,
    ) -> TemplateData:
        template = renderable.template
        config_dict = get_user_config()
        context_file = template.path / "cookiecutter.json"

        context = generate_context(
            context_file=context_file,
            default_context=config_dict["default_context"],
            extra_context=renderable.data,
        )
        context["cookiecutter"] = prompt_for_config(context, no_input)
        context["cookiecutter"]["_template"] = template.path

        generate_files(
            repo_dir=str(template.path),
            context=context,
            overwrite_if_exists=False,
            skip_if_file_exists=False,
            output_dir=str(renderable.out_root),
        )

        used_data = dict(context["cookiecutter"])
        used_data.pop("_template")

        return used_data
