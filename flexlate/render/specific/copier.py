from collections import ChainMap
from pathlib import Path
from typing import Any, Dict, Final, Sequence

import yaml
from copier import copy_local
from copier.config.factory import filter_config, verify_minimum_version
from copier.config.objects import ConfigData, EnvOps
from copier.config.user_data import load_config_data, query_user_data

from flexlate.render.renderable import Renderable
from flexlate.render.specific.base import SpecificTemplateRenderer
from flexlate.temp_path import create_temp_path
from flexlate.template.copier import CopierTemplate
from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData

exclude_copier_keys: Final[Sequence[str]] = ("now", "make_secret", "_folder_name")


class CopierRenderer(SpecificTemplateRenderer[CopierTemplate]):
    _template_cls = CopierTemplate
    _template_type = TemplateType.COPIER

    def render(
        self,
        renderable: Renderable[CopierTemplate],
        no_input: bool = False,
    ) -> TemplateData:
        template = renderable.template
        conf = _make_config_by_adding_defaults_then_prompting_user(
            str(template.path),
            str(renderable.out_root),
            data=renderable.data,
            no_input=no_input,
        )
        copy_local(conf=conf)
        return _extract_template_data_from_copier_config(conf)

    def render_string(
        self,
        string: str,
        renderable: Renderable[CopierTemplate],
    ) -> str:
        template = renderable.template

        with create_temp_path() as temp_template_path:
            copier_config_path = _find_copier_yaml_path(template.path)
            with open(copier_config_path, "r") as f:
                copier_config = yaml.safe_load(f)
            _modify_copier_config_yaml_to_remove_tasks(copier_config)
            config_out_path = temp_template_path / copier_config_path.name
            config_out_path.write_text(yaml.dump(copier_config))
            temp_template_file_path = (
                temp_template_path
                / template.render_relative_root_in_template
                / "temp.txt"
            )
            if not temp_template_file_path.parent.exists():
                temp_template_file_path.parent.mkdir(parents=True)
            temp_template_file_path.write_text(string)

            with create_temp_path() as temp_output_path:
                conf = _make_config_by_adding_defaults_then_prompting_user(
                    str(temp_template_path),
                    str(temp_output_path),
                    data=renderable.data,
                    no_input=True,
                )
                copy_local(conf=conf)
                temp_output_file_path = temp_output_path / "temp.txt"
                output = temp_output_file_path.read_text()
        return output


def _modify_copier_config_yaml_to_remove_tasks(
    copier_config: Dict[str, Any]
) -> Dict[str, Any]:
    if "_tasks" in copier_config:
        del copier_config["_tasks"]
    return copier_config


def _find_copier_yaml_path(template_root: Path) -> Path:
    copier_yaml_path = template_root / "copier.yml"
    if not copier_yaml_path.exists():
        copier_yaml_path = template_root / "copier.yaml"
    if not copier_yaml_path.exists():
        raise FileNotFoundError(
            f"Could not find copier.yml or copier.yaml in {template_root}"
        )
    return copier_yaml_path


def _extract_template_data_from_copier_config(config: ConfigData) -> TemplateData:
    raw_data = dict(config.data)
    return {
        key: value for key, value in raw_data.items() if key not in exclude_copier_keys
    }


def _make_config_by_adding_defaults_then_prompting_user(
    src_path: str, dst_path: str, data: TemplateData, no_input: bool = False
) -> ConfigData:
    """
    NOTE: Adapted from copier.config.factory.make_config
    """
    init_args: Dict[str, Any] = {}
    init_args["original_src_path"] = src_path
    init_args["src_path"] = src_path
    init_args["dst_path"] = dst_path

    # Skipped logic around VCS as we are always working with a local repo by this point

    file_data = load_config_data(src_path, quiet=True)

    try:
        verify_minimum_version(file_data["_min_copier_version"])
    except KeyError:
        pass

    template_config_data, questions_data = filter_config(file_data)
    init_args["data_from_template_defaults"] = {
        k: v.get("default") for k, v in questions_data.items()
    }
    init_args["envops"] = EnvOps(**template_config_data.get("envops", {}))

    init_args["data_from_init"] = ChainMap(
        query_user_data(
            {k: v for k, v in questions_data.items() if k in data},
            {},
            data,
            False,
            init_args["envops"],
        ),
        data,
    )
    init_args["data_from_asking_user"] = query_user_data(
        questions_data,
        # This is the main difference from copier.config.factory.make_config
        # In that function, it will use data_from_init (which includes passed data)
        # as forced_answers_data, meaning it will not prompt. It uses data_from_answers_file
        # to provide the defaults for prompts. Here we are not using the answers file, so
        # we use data_from_init as last_answers_data to provide defaults and do not force
        # any answers (so all prompts appear)
        init_args["data_from_init"],
        {},
        not no_input,
        init_args["envops"],
    )
    return ConfigData(**ChainMap(init_args, template_config_data))
