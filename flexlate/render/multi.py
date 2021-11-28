import os
import shutil
import tempfile
from pathlib import Path
from typing import Sequence, Optional, List, Dict

from flexlate.exc import InvalidTemplateClassException, RendererNotFoundException
from flexlate.render.specific.base import SpecificTemplateRenderer
from flexlate.render.specific.cookiecutter import CookiecutterRenderer
from flexlate.template.base import Template
from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData

renderers = [CookiecutterRenderer()]


class MultiRenderer:

    # TODO: register method to add user-defined template types

    def render(
        self,
        templates: Sequence[Template],
        data: Optional[Sequence[TemplateData]] = None,
        out_path: Path = Path("."),
        no_input: bool = False,
    ) -> List[TemplateData]:
        data = data or []
        out_data: List[TemplateData] = []
        with tempfile.TemporaryDirectory() as d:
            temp_root = Path(d)
            temp_folders: List[Path] = []
            for i, template in enumerate(templates):
                renderer = _get_specific_renderer(template)
                temp_folder = temp_root / f"{i + 1}-{template.name}"
                temp_folders.append(temp_folder)
                try:
                    in_data = data[i]
                except IndexError:
                    in_data = {}
                template_data = renderer.render(
                    template, data=in_data, out_path=temp_folder, no_input=no_input
                )
                out_data.append(template_data)
            _merge_file_trees(temp_folders, out_path)
        return out_data


def _get_specific_renderer(template: Template) -> SpecificTemplateRenderer:
    if template._type == TemplateType.BASE:
        raise InvalidTemplateClassException(
            f"No renderer for template type base, did you remember to override _type when defining the template type? {template}"
        )
    for renderer in renderers:
        if renderer._template_type == template._type:
            return renderer
    raise RendererNotFoundException(f"No registered renderer for template {template}")


def _merge_file_trees(dirs: Sequence[Path], out_dir: Path):
    for directory in dirs:
        _copy_files_to_directory(directory, out_dir)


def _copy_files_to_directory(dir: Path, out_dir: Path):
    for root, folders, files in os.walk(dir):
        in_folder = Path(root)
        relative_path = in_folder.relative_to(dir)
        out_folder = out_dir / relative_path
        if not out_folder.exists():
            out_folder.mkdir()
        for file in files:
            in_path = in_folder / file
            out_path = out_folder / file
            if out_path.exists():
                content = in_path.read_text()
                with open(out_path, mode="a") as f:
                    f.write(content)
            else:
                shutil.copy(in_path, out_path)
