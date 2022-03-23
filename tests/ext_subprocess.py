import shlex
import subprocess
from typing import Dict, Optional, Union, List

from flexlate.template_data import TemplateData


def run(
    command: str, input_data: Optional[Dict[str, str]] = None
) -> subprocess.CompletedProcess:
    split_command = shlex.split(command)
    input = get_text_input_from_data(input_data)
    return subprocess.run(split_command, check=True, input=input, encoding="utf8")


def get_text_input_from_data(
    input_data: Optional[Union[TemplateData, List[TemplateData]]]
) -> Optional[str]:
    if input_data is None:
        return None
    if isinstance(input_data, list):
        return "\n".join(_template_data_to_text_input(data) for data in input_data)
    return _template_data_to_text_input(input_data)


def _template_data_to_text_input(input_data: TemplateData) -> str:
    return "\n".join(str(value) for value in input_data.values())
