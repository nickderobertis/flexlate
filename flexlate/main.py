from pathlib import Path
from typing import Optional, List, Sequence

from git import Repo

from flexlate import exc
from flexlate.adder import Adder
from flexlate.add_mode import AddMode
from flexlate.branch_update import get_flexlate_branch_name
from flexlate.checker import Checker, CheckResults, CheckResultsRenderable
from flexlate.config_manager import ConfigManager
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.error_handler import simple_output_for_exceptions
from flexlate.finder.multi import MultiFinder
from flexlate.logger import log
from flexlate.merger import Merger
from flexlate.pusher import Pusher
from flexlate.remover import Remover
from flexlate.render.multi import MultiRenderer
from flexlate.styles import console
from flexlate.syncer import Syncer
from flexlate.template.base import Template
from flexlate.template_data import TemplateData
from flexlate.transactions.transaction import FlexlateTransaction, TransactionType
from flexlate.transactions.undoer import Undoer
from flexlate.update.main import Updater

log.debug("Flexlate debug logging enabled")


class Flexlate:
    def __init__(
        self,
        quiet: bool = False,
        adder: Adder = Adder(),
        checker: Checker = Checker(),
        remover: Remover = Remover(),
        config_manager: ConfigManager = ConfigManager(),
        merger: Merger = Merger(),
        finder: MultiFinder = MultiFinder(),
        pusher: Pusher = Pusher(),
        renderer: MultiRenderer = MultiRenderer(),
        syncer: Syncer = Syncer(),
        updater: Updater = Updater(),
        undoer: Undoer = Undoer(),
    ):
        self.quiet = quiet
        # Let rich handle suppressing output
        console.quiet = quiet

        self.adder = adder
        self.checker = checker
        self.remover = remover
        self.config_manager = config_manager
        self.merger = merger
        self.finder = finder
        self.pusher = pusher
        self.renderer = renderer
        self.syncer = syncer
        self.updater = updater
        self.undoer = undoer

    @simple_output_for_exceptions(exc.GitRepoDirtyException)
    def init_project(
        self,
        path: Path = Path("."),
        default_add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        user: bool = False,
        remote: str = "origin",
    ):
        repo = Repo(path)
        self.adder.init_project_and_add_to_branches(
            repo,
            default_add_mode=default_add_mode,
            user=user,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
            remote=remote,
            config_manager=self.config_manager,
        )

    def init_project_from(
        self,
        template_path: str,
        path: Path = Path("."),
        template_version: Optional[str] = None,
        data: Optional[TemplateData] = None,
        default_folder_name: str = "project",
        no_input: bool = False,
        default_add_mode: AddMode = AddMode.LOCAL,
        remote: str = "origin",
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    ) -> str:
        transaction = FlexlateTransaction(
            type=TransactionType.ADD_SOURCE_AND_OUTPUT,
            target=template_path,
            out_root=path,
        )
        template = self.finder.find(template_path, version=template_version)
        return self.adder.init_project_from_template_source_path(
            template,
            transaction,
            path=path,
            target_version=template_version,
            default_folder_name=default_folder_name,
            data=data,
            no_input=no_input,
            default_add_mode=default_add_mode,
            remote=remote,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
            config_manager=self.config_manager,
            updater=self.updater,
            renderer=self.renderer,
            syncer=self.syncer,
        )

    @simple_output_for_exceptions(
        exc.GitRepoDirtyException, exc.TemplateSourceWithNameAlreadyExistsException
    )
    def add_template_source(
        self,
        path: str,
        name: Optional[str] = None,
        target_version: Optional[str] = None,
        template_root: Path = Path("."),
        add_mode: Optional[AddMode] = None,
    ):
        transaction = FlexlateTransaction(
            type=TransactionType.ADD_SOURCE, target=name or path, out_root=template_root
        )
        project_config = self.config_manager.load_project_config(template_root)
        add_mode = add_mode or project_config.default_add_mode
        template = self.finder.find(path, version=target_version)
        if name:
            template.name = name
        repo = Repo(project_config.path)
        self.adder.add_template_source(
            repo,
            template,
            transaction,
            target_version=target_version,
            out_root=template_root,
            merged_branch_name=get_flexlate_branch_name(
                repo, project_config.merged_branch_name
            ),
            base_merged_branch_name=project_config.merged_branch_name,
            template_branch_name=get_flexlate_branch_name(
                repo, project_config.template_branch_name
            ),
            base_template_branch_name=project_config.template_branch_name,
            add_mode=add_mode,
            remote=project_config.remote,
            config_manager=self.config_manager,
        )

    @simple_output_for_exceptions(exc.GitRepoDirtyException)
    def remove_template_source(
        self,
        template_name: str,
        template_root: Path = Path("."),
    ):
        transaction = FlexlateTransaction(
            type=TransactionType.REMOVE_SOURCE,
            target=template_name,
            out_root=template_root,
        )
        project_config = self.config_manager.load_project_config(template_root)
        repo = Repo(project_config.path)
        self.remover.remove_template_source(
            repo,
            template_name,
            transaction,
            out_root=template_root,
            merged_branch_name=get_flexlate_branch_name(
                repo, project_config.merged_branch_name
            ),
            base_merged_branch_name=project_config.merged_branch_name,
            template_branch_name=get_flexlate_branch_name(
                repo, project_config.template_branch_name
            ),
            base_template_branch_name=project_config.template_branch_name,
            add_mode=project_config.default_add_mode,
            remote=project_config.remote,
            config_manager=self.config_manager,
        )

    @simple_output_for_exceptions(
        exc.GitRepoDirtyException, exc.TemplateNotRegisteredException
    )
    def apply_template_and_add(
        self,
        name: str,
        data: Optional[TemplateData] = None,
        out_root: Path = Path("."),
        add_mode: Optional[AddMode] = None,
        no_input: bool = False,
    ):
        transaction = FlexlateTransaction(
            type=TransactionType.ADD_OUTPUT, target=name, out_root=out_root, data=data
        )
        project_config = self.config_manager.load_project_config(out_root)
        add_mode = add_mode or project_config.default_add_mode
        template = self.config_manager.get_template_by_name(
            name, project_root=project_config.path
        )
        repo = Repo(project_config.path)
        self.adder.apply_template_and_add(
            repo,
            template,
            transaction,
            data=data,
            out_root=out_root,
            add_mode=add_mode,
            no_input=no_input,
            merged_branch_name=get_flexlate_branch_name(
                repo, project_config.merged_branch_name
            ),
            base_merged_branch_name=project_config.merged_branch_name,
            template_branch_name=get_flexlate_branch_name(
                repo, project_config.template_branch_name
            ),
            base_template_branch_name=project_config.template_branch_name,
            remote=project_config.remote,
            config_manager=self.config_manager,
            renderer=self.renderer,
            updater=self.updater,
        )

    @simple_output_for_exceptions(exc.GitRepoDirtyException)
    def remove_applied_template_and_output(
        self,
        template_name: str,
        out_root: Path = Path("."),
    ):
        transaction = FlexlateTransaction(
            type=TransactionType.REMOVE_OUTPUT, target=template_name, out_root=out_root
        )
        project_config = self.config_manager.load_project_config(out_root)
        repo = Repo(project_config.path)

        self.remover.remove_applied_template_and_output(
            repo,
            template_name,
            transaction,
            out_root=out_root,
            add_mode=project_config.default_add_mode,
            merged_branch_name=get_flexlate_branch_name(
                repo, project_config.merged_branch_name
            ),
            base_merged_branch_name=project_config.merged_branch_name,
            template_branch_name=get_flexlate_branch_name(
                repo, project_config.template_branch_name
            ),
            base_template_branch_name=project_config.template_branch_name,
            remote=project_config.remote,
            config_manager=self.config_manager,
            updater=self.updater,
            renderer=self.renderer,
        )

    @simple_output_for_exceptions(exc.GitRepoDirtyException)
    def update(
        self,
        names: Optional[List[str]] = None,
        data: Optional[Sequence[TemplateData]] = None,
        no_input: bool = False,
        abort_on_conflict: bool = False,
        project_path: Path = Path("."),
    ):
        transaction = FlexlateTransaction(
            type=TransactionType.UPDATE,
            target=", ".join(names) if names is not None else None,
            data=data,
        )
        project_config = self.config_manager.load_project_config(project_path)
        templates: List[Template]
        if names:
            # User wants to update targeted template sources
            templates = [
                self.config_manager.get_template_by_name(
                    name, project_root=project_config.path
                )
                for name in names
            ]
        else:
            # User wants to update all templates
            templates = self.config_manager.get_all_templates(
                project_root=project_config.path
            )
        self.updater.update_passed_templates_to_target_versions(
            templates,
            project_root=project_config.path,
            finder=self.finder,
            config_manager=self.config_manager,
        )
        updates = self.updater.get_updates_for_templates(
            templates,
            data=data,
            config_manager=self.config_manager,
            project_root=project_config.path,
        )

        repo = Repo(project_config.path)
        self.updater.update(
            repo,
            updates,
            transaction,
            no_input=no_input,
            abort_on_conflict=abort_on_conflict,
            merged_branch_name=get_flexlate_branch_name(
                repo, project_config.merged_branch_name
            ),
            base_merged_branch_name=project_config.merged_branch_name,
            template_branch_name=get_flexlate_branch_name(
                repo, project_config.template_branch_name
            ),
            base_template_branch_name=project_config.template_branch_name,
            renderer=self.renderer,
            config_manager=self.config_manager,
        )

    @simple_output_for_exceptions(exc.GitRepoDirtyException)
    def undo(self, num_operations: int = 1, project_path: Path = Path(".")):
        project_config = self.config_manager.load_project_config(project_path)
        repo = Repo(project_config.path)
        self.undoer.undo_transactions(
            repo,
            num_transactions=num_operations,
            merged_branch_name=get_flexlate_branch_name(
                repo, project_config.merged_branch_name
            ),
            base_merged_branch_name=project_config.merged_branch_name,
            template_branch_name=get_flexlate_branch_name(
                repo, project_config.template_branch_name
            ),
            base_template_branch_name=project_config.template_branch_name,
        )

    @simple_output_for_exceptions(
        exc.GitRepoDirtyException, exc.UnnecessarySyncException
    )
    def sync(
        self,
        prompt: bool = False,
        project_path: Path = Path("."),
    ):
        project_config = self.config_manager.load_project_config(project_path)
        repo = Repo(project_config.path)
        transaction = FlexlateTransaction(
            type=TransactionType.SYNC,
        )
        self.syncer.sync_local_changes_to_flexlate_branches(
            repo,
            transaction,
            merged_branch_name=get_flexlate_branch_name(
                repo, project_config.merged_branch_name
            ),
            base_merged_branch_name=project_config.merged_branch_name,
            template_branch_name=get_flexlate_branch_name(
                repo, project_config.template_branch_name
            ),
            base_template_branch_name=project_config.template_branch_name,
            no_input=not prompt,
            updater=self.updater,
            renderer=self.renderer,
            config_manager=self.config_manager,
        )

    def merge_flexlate_branches(
        self,
        branch_name: Optional[str] = None,
        delete: bool = True,
        project_path: Path = Path("."),
    ):
        project_config = self.config_manager.load_project_config(project_path)
        repo = Repo(project_config.path)
        self.merger.merge_flexlate_branches(
            repo,
            branch_name,
            delete=delete,
            merged_branch_name=project_config.merged_branch_name,
            template_branch_name=project_config.template_branch_name,
        )

    def push_main_flexlate_branches(
        self,
        remote: Optional[str] = None,
        project_path: Path = Path("."),
    ):
        project_config = self.config_manager.load_project_config(project_path)
        use_remote = remote or project_config.remote
        repo = Repo(project_config.path)
        self.pusher.push_main_flexlate_branches(
            repo,
            use_remote,
            merged_branch_name=project_config.merged_branch_name,
            template_branch_name=project_config.template_branch_name,
        )

    def push_feature_flexlate_branches(
        self,
        feature_branch: Optional[str] = None,
        remote: str = "origin",
        project_path: Path = Path("."),
    ):
        project_config = self.config_manager.load_project_config(project_path)
        repo = Repo(project_config.path)
        self.pusher.push_feature_flexlate_branches(
            repo,
            feature_branch,
            remote,
            merged_branch_name=project_config.merged_branch_name,
            template_branch_name=project_config.template_branch_name,
        )

    @simple_output_for_exceptions(exc.TemplateNotRegisteredException)
    def check(
        self, names: Optional[Sequence[str]] = None, project_path: Path = Path(".")
    ) -> CheckResults:
        check_results = self.checker.find_new_versions_for_template_sources(
            names,
            project_root=project_path,
            config_manager=self.config_manager,
            finder=self.finder,
        )
        console.print(CheckResultsRenderable(results=check_results.updates))
        return check_results

    # TODO: list template sources, list applied templates
    # TODO: Update target versions in template sources
