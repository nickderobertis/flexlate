from pathlib import Path
from typing import Sequence, Optional, Dict, Any, List

from pydantic import BaseModel

from flexlate.config_manager import ConfigManager
from flexlate.finder.multi import MultiFinder


class CheckResult(BaseModel):
    source_name: str
    existing_version: str
    latest_version: str

    @property
    def has_update(self) -> bool:
        return self.existing_version != self.latest_version


class CheckResults(BaseModel):
    results: List[CheckResult]

    @property
    def updates(self) -> List[CheckResult]:
        return [result for result in self.results if result.has_update]

    @property
    def update_version_dict(self) -> Dict[str, str]:
        return {result.source_name: result.latest_version for result in self.updates}

    @property
    def has_updates(self) -> bool:
        return len(self.updates) != 0


class Checker:
    def find_new_versions_for_template_sources(
        self,
        names: Optional[Sequence[str]] = None,
        project_root: Path = Path("."),
        config_manager: ConfigManager = ConfigManager(),
        finder: MultiFinder = MultiFinder(),
    ) -> CheckResults:
        sources = config_manager.get_template_sources(names, project_root=project_root)
        results: List[CheckResult] = []
        for source in sources:
            kwargs: Dict[str, Any] = {}
            if source.target_version:
                kwargs.update(version=source.target_version)
            new_template = finder.find(str(source.update_location), **kwargs)
            results.append(
                CheckResult(
                    source_name=source.name,
                    existing_version=source.version,
                    latest_version=new_template.version,
                )
            )
        return CheckResults(results=results)
