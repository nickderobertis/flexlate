from pathlib import Path
from typing import Sequence, List

from flexlate.config import FlexlateConfig
from flexlate.types import TemplateData


class ConfigManager:
    def load_config(self, project_root: Path = Path(".")) -> FlexlateConfig:
        return FlexlateConfig.from_dir_including_nested(project_root)

    def get_data(self, names: Sequence[str]) -> List[TemplateData]:
        pass