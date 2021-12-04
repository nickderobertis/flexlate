import abc
from pathlib import Path
from typing import Optional

from flexlate.template.hashing import md5_dir
from flexlate.template.types import TemplateType
from flexlate.template_config.base import TemplateConfig


class Template(abc.ABC):
    # Override this in subclasses
    _type: TemplateType = TemplateType.BASE

    def __init__(
        self,
        config: TemplateConfig,
        path: Path,
        name: Optional[str] = None,
        version: Optional[str] = None,
        target_version: Optional[str] = None,
        git_url: Optional[str] = None,
    ):
        self.config = config
        self.path = path
        self.git_url = git_url
        self.target_version = target_version
        self.name = name or self.default_name
        self.version = version or self.folder_hash

    @property
    def default_name(self) -> str:
        return self.path.name

    @property
    def folder_hash(self) -> str:
        return md5_dir(self.path)
