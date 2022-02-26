from pathlib import Path
from typing import Sequence, Optional, Dict, Any

from flexlate.config_manager import ConfigManager
from flexlate.finder.multi import MultiFinder


class Checker:
    def find_new_versions_for_template_sources(
        self,
        names: Optional[Sequence[str]] = None,
        project_root: Path = Path("."),
        config_manager: ConfigManager = ConfigManager(),
        finder: MultiFinder = MultiFinder(),
    ) -> Dict[str, str]:
        sources = config_manager.get_template_sources(names, project_root=project_root)
        new_versions: Dict[str, str] = {}
        for source in sources:
            kwargs: Dict[str, Any] = {}
            if source.target_version:
                kwargs.update(version=source.target_version)
            new_template = finder.find(str(source.update_location), **kwargs)
            if source.version != new_template.version:
                # Source needs to be upgraded
                new_versions[source.name] = new_template.version
        return new_versions
