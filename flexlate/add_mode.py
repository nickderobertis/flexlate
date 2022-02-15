from enum import Enum
from pathlib import Path


class AddMode(str, Enum):
    LOCAL = "local"
    PROJECT = "project"
    USER = "user"


def get_expanded_out_root(
    out_root: Path,
    project_root: Path,
    render_relative_root_in_output: Path,
    add_mode: AddMode,
) -> Path:
    if add_mode == AddMode.USER:
        # Always use full absolute paths for user
        return out_root.absolute()
    if add_mode == AddMode.PROJECT:
        # Return a project-relative path for project
        return out_root.absolute().relative_to(project_root.absolute())
    if add_mode == AddMode.LOCAL:
        # Needs to be the relative path to get back to template root from the
        # render relative root
        return Path(*[".." for _ in range(len(render_relative_root_in_output.parts))])
    raise ValueError(f"unsupported add mode {add_mode}")
