from pathlib import Path

from flexlate.template_config.base import TemplateConfig
from flexlate.template_data import TemplateData


class CopierConfig(TemplateConfig):
    def __init__(self, defaults: TemplateData, render_relative_root: Path = Path(".")):
        super().__init__(defaults)
        self.render_relative_root = render_relative_root
