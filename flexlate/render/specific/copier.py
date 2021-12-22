from pathlib import Path
from typing import Optional, Sequence, Final

from copier import copy_local
from copier.config import make_config
from copier.config.objects import ConfigData

from flexlate.render.renderable import Renderable
from flexlate.render.specific.base import SpecificTemplateRenderer
from flexlate.template.copier import CopierTemplate
from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData

exclude_copier_keys: Final[Sequence[str]] = ("now", "make_secret", "_folder_name")


class CopierRenderer(SpecificTemplateRenderer[CopierTemplate]):
    _template_cls = CopierTemplate
    _template_type = TemplateType.COPIER

    def render(
        self,
        renderable: Renderable[CopierTemplate],
        no_input: bool = False,
    ) -> TemplateData:
        template = renderable.template
        conf = make_config(
            str(template.path),
            str(renderable.out_root),
            force=no_input,
            data=renderable.data,
        )
        copy_local(conf=conf)
        return _extract_template_data_from_copier_config(conf)


def _extract_template_data_from_copier_config(config: ConfigData) -> TemplateData:
    raw_data = dict(config.data)
    return {
        key: value for key, value in raw_data.items() if key not in exclude_copier_keys
    }
