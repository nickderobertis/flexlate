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
        template_source_path: Optional[str] = None,
        render_relative_root_in_output: Path = Path("."),
        render_relative_root_in_template: Path = Path("."),
    ):
        self.config = config
        self.path = path
        self.git_url = git_url
        self.target_version = target_version
        self.name = name or self.default_name
        self.version = version or self.folder_hash
        self.template_source_path = template_source_path or path
        self.render_relative_root_in_output = render_relative_root_in_output
        self.render_relative_root_in_template = render_relative_root_in_template

    @property
    def default_name(self) -> str:
        return self.path.name

    @property
    def folder_hash(self) -> str:
        return md5_dir(self.path)

    def __eq__(self, other):
        try:
            return all(
                [
                    self.config == other.config,
                    self.path == other.path,
                    self.git_url == other.git_url,
                    self.target_version == other.target_version,
                    self.name == other.name,
                    self.version == other.version,
                    self.template_source_path == other.template_source_path,
                    self.render_relative_root_in_output
                    == other.render_relative_root_in_output,
                    self.render_relative_root_in_template
                    == other.render_relative_root_in_template,
                ]
            )
        except AttributeError:
            return False
