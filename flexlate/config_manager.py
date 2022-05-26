import os
from pathlib import Path
from typing import Sequence, List, Optional, Tuple, Set, Dict, Callable

from flexlate.add_mode import AddMode, get_expanded_out_root
from flexlate.config import (
    FlexlateConfig,
    TemplateSource,
    AppliedTemplateConfig,
    AppliedTemplateWithSource,
    FlexlateProjectConfig,
    ProjectConfig,
    TemplateSourceWithTemplates,
)
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import (
    FlexlateConfigFileNotExistsException,
    TemplateLookupException,
    InvalidTemplateDataException,
    TemplateNotRegisteredException,
    CannotLoadConfigException,
    FlexlateProjectConfigFileNotExistsException,
    CannotRemoveTemplateSourceException,
    CannotRemoveAppliedTemplateException,
)
from flexlate.path_ops import (
    location_relative_to_new_parent,
    make_absolute_path_from_possibly_relative_to_another_path,
)
from flexlate.render.multi import MultiRenderer
from flexlate.render.renderable import Renderable
from flexlate.template.base import Template
from flexlate.template_data import TemplateData, merge_data
from flexlate.update.template import TemplateUpdate, data_from_template_updates


class ConfigManager:
    def load_config(
        self, project_root: Path = Path("."), adjust_applied_paths: bool = True
    ) -> FlexlateConfig:
        return FlexlateConfig.from_dir_including_nested(
            project_root, adjust_applied_paths=adjust_applied_paths
        )

    def save_config(self, config: FlexlateConfig):
        config.save()

    def load_specific_projects_config(self, path: Path = Path("."), user: bool = False):
        use_path: Optional[Path] = None
        if not user:
            use_path = path / FlexlateProjectConfig._settings.config_file_name
        # else, let py-app-conf figure out the path for user config
        return FlexlateProjectConfig.load_or_create(use_path)

    def load_projects_config(self, path: Path = Path(".")) -> FlexlateProjectConfig:
        # TODO: more efficient algorithm for finding project config
        try:
            config = FlexlateProjectConfig.load_recursive(path)
        except FileNotFoundError:
            raise FlexlateProjectConfigFileNotExistsException(
                f"could not find a projects config file in any "
                f"parent directory of path {path} or in the user directory"
            )
        # The found config might not have this project's config in it, need to check
        try:
            config.get_project_for_path(path)
        except FlexlateProjectConfigFileNotExistsException as e:
            # Project was not in this config file. Keep going up to parents
            # to check for more config files
            if path.parent == path:
                # We have hit the root path, and still have not found the config.
                # It must not exist, so raise the error
                raise e
            return self.load_projects_config(path.parent)

        return config

    def load_project_config(self, path: Path = Path(".")) -> ProjectConfig:
        use_path = path.resolve()
        projects_config = self.load_projects_config(path=use_path)
        return projects_config.get_project_for_path(use_path)

    def save_projects_config(self, config: FlexlateProjectConfig):
        config.save()

    def add_project(
        self,
        path: Path = Path("."),
        default_add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        user: bool = False,
        remote: str = "origin",
    ):
        config = self.load_specific_projects_config(path, user)
        output_path = path.absolute() if user else Path(".")
        project_config = ProjectConfig(
            path=output_path,
            default_add_mode=default_add_mode,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
            remote=remote,
        )
        config.projects.append(project_config)
        self.save_projects_config(config)

    def get_applied_templates_with_sources(
        self,
        relative_to: Optional[Path] = None,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> List[AppliedTemplateWithSource]:
        config = config or self.load_config(project_root)
        sources = config.template_sources_dict
        applied_template_with_sources: List[AppliedTemplateWithSource] = []
        for applied_template in config.applied_templates:
            source = sources[applied_template.name]
            if (
                relative_to is not None
                and source.git_url is None
                and not Path(source.path).is_absolute()
            ):
                new_path = (relative_to / Path(source.path)).resolve()
                use_source = source.copy(update=dict(path=new_path))
            else:
                use_source = source
            applied_template_with_sources.append(
                AppliedTemplateWithSource(
                    applied_template=applied_template, source=use_source
                )
            )
        return applied_template_with_sources

    def get_all_renderables(
        self,
        relative_to: Optional[Path] = None,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> List[Renderable]:
        config = config or self.load_config(project_root)
        return [
            Renderable.from_applied_template_with_source(applied_with_source)
            for applied_with_source in self.get_applied_templates_with_sources(
                relative_to=relative_to, project_root=project_root, config=config
            )
        ]

    def get_renderables_for_updates(
        self,
        updates: Sequence[TemplateUpdate],
        project_root: Path = Path("."),
        adjust_root: bool = True,
    ) -> List[Renderable]:
        return [
            update.to_renderable(project_root=project_root, adjust_root=adjust_root)
            for update in updates
        ]

    def get_all_templates(
        self,
        relative_to: Optional[Path] = None,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> List[Template]:
        renderables = self.get_all_renderables(
            relative_to=relative_to, project_root=project_root, config=config
        )
        templates: List[Template] = []
        for renderable in renderables:
            if renderable.template in templates:
                continue
            templates.append(renderable.template)
        return templates

    def get_data_for_updates(
        self,
        updates: Sequence[TemplateUpdate],
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> List[TemplateData]:
        config = config or self.load_config(project_root)
        data: List[TemplateData] = []
        for update in updates:
            applied_template = config.get_applied_template_by_update(update)
            data.append(applied_template.data)
        return data

    def get_no_op_updates(
        self,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> List[TemplateUpdate]:
        config = config or self.load_config(project_root)
        updates: List[TemplateUpdate] = []
        sources = config.template_sources_dict
        for child_config in config.child_configs:
            for i, applied_template in enumerate(child_config.applied_templates):
                source = sources[applied_template.name]
                template = source.to_template(version=applied_template.version)
                template.version = applied_template.version
                updates.append(
                    TemplateUpdate(
                        template=template,
                        config_location=child_config.settings.config_location,
                        index=i,
                        data=applied_template.data,
                    )
                )
        return updates

    def update_templates(
        self,
        updates: Sequence[TemplateUpdate],
        project_root: Path = Path("."),
        use_template_source_path: bool = True,
    ):
        # Don't adjust applied paths, as we are not doing anything with them and writing them back
        config = self.load_config(project_root, adjust_applied_paths=False)
        existing_data = self.get_data_for_updates(updates, project_root, config)
        template_data = data_from_template_updates(updates)
        all_data = merge_data(template_data, existing_data)
        if len(updates) != len(all_data):
            raise InvalidTemplateDataException(
                f"length of templates and template data must match. got updates {updates} and data {template_data}"
            )

        for update, data in zip(updates, all_data):

            def update_applied_template(applied_template: AppliedTemplateConfig):
                applied_template.data = update.data or {}
                applied_template.version = update.template.version

            def update_template_source(template_source: TemplateSource):
                template_source.version = update.template.version
                template_source.type = update.template._type
                template_source.render_relative_root_in_output = (
                    update.template.render_relative_root_in_output
                )
                template_source.render_relative_root_in_template = (
                    update.template.render_relative_root_in_template
                )

                # For remote templates, always bring over the new path
                # For local templates, the use_template_source_path option toggles between
                # using the original string from the template source, and the
                # detected absolute location in the template.
                template_source.path = (
                    str(update.template.template_source_path)
                    if use_template_source_path
                    else str(update.template.path)
                )

            config.update_applied_template(
                update_applied_template, update.config_location, update.index
            )
            config.update_template_source(update_template_source, update.template.name)
        self.save_config(config)

    def add_template_source(
        self,
        template: Template,
        config_path: Path,
        target_version: Optional[str] = None,
        project_root: Path = Path("."),
    ):
        config = self.load_config(project_root=project_root, adjust_applied_paths=False)
        source = TemplateSource.from_template(
            template,
            target_version=target_version,
        )
        config.add_template_source(source, config_path)
        self.save_config(config)

    def remove_template_source(
        self,
        template_name: str,
        config_path: Path,
        project_root: Path = Path("."),
    ):
        config = self.load_config(project_root=project_root, adjust_applied_paths=False)
        if self._applied_template_exists_in_project(
            template_name, project_root=project_root, config=config
        ):
            # TODO: Improve error message for can't remove template source
            #  When can't remove template source due to existing applied template, determine paths where
            #  the existing applied templates are to inform the user what needs to be removed
            raise CannotRemoveTemplateSourceException(
                f"Cannot remove template source {template_name} as it has existing outputs"
            )

        config.remove_template_source(template_name, config_path)
        self.save_config(config)

    def _applied_template_exists_in_project(
        self,
        template_name: str,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ):
        config = config or self.load_config(project_root=project_root)
        for child_config in config.child_configs:
            for applied_template in child_config.applied_templates:
                if applied_template.name == template_name:
                    return True
        return False

    def add_applied_template(
        self,
        template: Template,
        config_path: Path,
        add_mode: AddMode,
        data: Optional[TemplateData] = None,
        project_root: Path = Path("."),
        out_root: Path = Path("."),
    ):
        config = self.load_config(project_root=project_root, adjust_applied_paths=False)
        applied = AppliedTemplateConfig(
            name=template.name,
            data=data or {},
            version=template.version,
            root=out_root,
            add_mode=add_mode,
        )
        config.add_applied_template(applied, config_path)
        self.save_config(config)

    def remove_applied_template(
        self,
        template_name: str,
        config_path: Path,
        project_root: Path = Path("."),
        out_root: Path = Path("."),
        orig_project_root: Path = Path("."),
    ):
        """

        :param template_name:
        :param config_path:
        :param project_root: The root of the current working project (may be a temp directory)
        :param out_root:
        :param orig_project_root: The root of the user's project (always stays the same, even
            when working in a temp directory)
        :return:
        """
        config = self.load_config(project_root=project_root, adjust_applied_paths=False)
        config.remove_applied_template(
            template_name,
            config_path,
            project_root=project_root,
            out_root=out_root,
            orig_project_root=orig_project_root,
        )
        self.save_config(config)

    def get_num_applied_templates_in_child_config(
        self, child_config_path: Path, project_root: Path = Path(".")
    ):
        config = self.load_config(project_root)
        return config.get_num_applied_templates_in_child_config(child_config_path)

    def get_template_sources(
        self,
        names: Optional[Sequence[str]] = None,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> List[TemplateSource]:
        config = config or self.load_config(project_root)
        if names:
            return [
                self._get_template_source_by_name(
                    name, project_root=project_root, config=config
                )
                for name in names
            ]
        return config.template_sources

    def _get_template_source_by_name(
        self,
        name: str,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> TemplateSource:
        config = config or self.load_config(project_root)
        try:
            source = config.template_sources_dict[name]
        except KeyError:
            raise TemplateNotRegisteredException(
                f"could not find template source with name {name}"
            )
        return source

    def get_template_by_name(
        self,
        name: str,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> Template:
        return self._get_template_source_by_name(
            name, project_root=project_root, config=config
        ).to_template()

    def template_source_exists(
        self,
        name: str,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> bool:
        try:
            self._get_template_source_by_name(
                name, project_root=project_root, config=config
            )
            return True
        except TemplateNotRegisteredException:
            return False

    def get_sources_with_templates(
        self,
        templates: Sequence[Template],
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> List[TemplateSourceWithTemplates]:
        config = config or self.load_config(project_root)
        sources_with_templates: Dict[str, TemplateSourceWithTemplates] = {}
        seen_sources: Set[str] = set()
        for template in templates:
            source = self._get_template_source_by_name(template.name, config=config)
            if source.name in seen_sources:
                sources_with_templates[source.name].templates.append(template)
            else:
                sources_with_templates[source.name] = TemplateSourceWithTemplates(
                    source=source, templates=[template]
                )
            seen_sources.add(source.name)
        return list(sources_with_templates.values())

    def move_applied_template(
        self,
        template_name: str,
        config_path: Path,
        new_config_path: Path,
        render_relative_root_in_output: Path,
        project_root: Path = Path("."),
        out_root: Path = Path("."),
        orig_project_root: Path = Path("."),
    ):
        config = self.load_config(project_root=project_root, adjust_applied_paths=False)
        config.move_applied_template(
            template_name,
            config_path,
            new_config_path,
            render_relative_root_in_output,
            out_root=out_root,
            orig_project_root=orig_project_root,
        )
        self.save_config(config)

    def move_template_source(
        self,
        template_name: str,
        config_path: Path,
        new_config_path: Path,
        project_root: Path = Path("."),
    ):
        config = self.load_config(project_root=project_root, adjust_applied_paths=False)
        config.move_template_source(template_name, config_path, new_config_path)
        self.save_config(config)

    def _get_applied_templates_and_sources_with_local_add_mode(
        self,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> List[AppliedTemplateWithSource]:
        config = config or self.load_config(project_root=project_root)

        return [
            atws
            for atws in self.get_applied_templates_with_sources(
                project_root=project_root, config=config
            )
            if atws.applied_template.add_mode == AddMode.LOCAL
        ]

    def move_local_applied_templates_if_necessary(
        self,
        project_root: Path = Path("."),
        orig_project_root: Path = Path("."),
        renderer: MultiRenderer = MultiRenderer(),
    ):
        config = self.load_config(project_root=project_root)
        applied_templates_with_sources = (
            self._get_applied_templates_and_sources_with_local_add_mode(
                project_root=project_root, config=config
            )
        )
        for atwc in applied_templates_with_sources:
            source = atwc.source
            if source.is_local_template:
                # Move source back to orig project so that relative template
                # paths can be resolved
                source.path = str(
                    location_relative_to_new_parent(
                        Path(source.path), project_root, orig_project_root, project_root
                    ).resolve()
                )
            template = source.to_template()
            renderable = Renderable.from_applied_template_with_source(atwc)
            new_relative_out_root = Path(
                renderer.render_string(
                    str(template.render_relative_root_in_output), renderable
                )
            )
            orig_config_path = atwc.applied_template._config_file_location

            render_root = (
                orig_config_path.parent / atwc.applied_template._orig_root
            ).resolve()
            new_config_path = render_root / new_relative_out_root / "flexlate.json"
            if orig_config_path == new_config_path:
                # No need to move, still in the same location
                continue

            # Must have different location now, move it
            # TODO: more efficient algorithm for updating locations of applied templates
            #  Currently it needs to find the template twice
            self.move_applied_template(
                atwc.source.name,
                orig_config_path,
                new_config_path,
                source.render_relative_root_in_output,
                project_root=project_root,
                out_root=atwc.applied_template._orig_root,
                orig_project_root=orig_project_root,
            )

    def update_template_sources(
        self,
        names: Sequence[str],
        updater: Callable[[TemplateSource], None],
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ):
        config = config or self.load_config(project_root, adjust_applied_paths=False)
        config.update_template_sources(updater, names)
        self.save_config(config)

    def update_template_source_version(
        self,
        name: str,
        target_version: Optional[str] = None,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ):
        config = config or self.load_config(project_root, adjust_applied_paths=False)

        def _update_template_source_version(source: TemplateSource):
            source.target_version = target_version

        self.update_template_sources(
            [name], _update_template_source_version, config=config
        )


def determine_config_path_from_roots_and_add_mode(
    out_root: Path = Path("."),
    project_root: Path = Path("."),
    add_mode: AddMode = AddMode.LOCAL,
) -> Path:
    if add_mode == AddMode.USER:
        return FlexlateConfig._settings.config_location
    if add_mode == AddMode.PROJECT:
        return project_root / "flexlate.json"
    if add_mode == AddMode.LOCAL:
        return out_root / "flexlate.json"
    raise ValueError(f"unexpected add mode {add_mode}")
