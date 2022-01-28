from typing import List

from click.testing import Result


def result_to_message(result: Result) -> str:
    output_parts: List[str] = []
    if result.stdout:
        output_parts.append(f"stdout:\n{result.stdout}")
    try:
        output_parts.append(f"sterr:\n{result.stderr}")
    except ValueError as e:
        if "stderr not separately captured" in str(e):
            pass
        else:
            raise e
    if result.exception:
        output_parts.append(f"exception:\n{result.exception}")
    return "\n".join(output_parts)
