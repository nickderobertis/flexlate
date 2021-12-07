from typing import Dict, Any, Sequence, List

TemplateData = Dict[str, Any]


def merge_data(
    overrides: Sequence[TemplateData], defaults: Sequence[TemplateData]
) -> List[TemplateData]:
    out_data: List[TemplateData] = []
    for i, default_data in enumerate(defaults):
        try:
            override_data = overrides[i]
        except IndexError:
            override_data = {}
        out_data.append({**default_data, **override_data})
    return out_data
