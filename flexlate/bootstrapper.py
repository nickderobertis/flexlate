from pathlib import Path
from typing import Optional

from git import Repo

from flexlate.add_mode import AddMode, get_expanded_out_root
from flexlate.adder import Adder
from flexlate.config_manager import (
    ConfigManager,
    determine_config_path_from_roots_and_add_mode,
)
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.ext_git import stage_and_commit_all
from flexlate.render.multi import MultiRenderer
from flexlate.styles import print_styled, INFO_STYLE, SUCCESS_STYLE
from flexlate.syncer import Syncer
from flexlate.template.base import Template
from flexlate.template_data import TemplateData
from flexlate.transactions.transaction import FlexlateTransaction
from flexlate.update.main import Updater


class Bootstrapper:
    def bootstrap_flexlate_init_from_existing_template(
        self,
        repo: Repo,
        template: Template,
        transaction: FlexlateTransaction,
        target_version: Optional[str] = None,
        data: Optional[TemplateData] = None,
        default_add_mode: AddMode = AddMode.LOCAL,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        remote: str = "origin",
        no_input: bool = False,
        adder: Adder = Adder(),
        config_manager: ConfigManager = ConfigManager(),
        renderer: MultiRenderer = MultiRenderer(),
        syncer: Syncer = Syncer(),
        updater: Updater = Updater(),
    ):
        if repo.working_dir is None:
            raise ValueError("repo working dir must not be None")
        project_root = Path(repo.working_dir)

        print_styled(
            f"Bootstrapping {project_root} into a Flexlate project based off the template from {template.template_source_path}",
            INFO_STYLE,
        )

        adder.init_project_and_add_to_branches(
            repo,
            default_add_mode=default_add_mode,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
            remote=remote,
            config_manager=config_manager,
        )
        adder.add_template_source(
            repo,
            template,
            transaction,
            target_version=target_version,
            out_root=project_root,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
            base_merged_branch_name=base_merged_branch_name,
            base_template_branch_name=base_template_branch_name,
            remote=remote,
            config_manager=config_manager,
        )
        adder.apply_template_and_add(
            repo,
            template,
            transaction,
            data=data,
            out_root=project_root,
            add_mode=AddMode.LOCAL,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
            base_merged_branch_name=base_merged_branch_name,
            base_template_branch_name=base_template_branch_name,
            no_input=no_input,
            remote=remote,
            config_manager=config_manager,
            updater=updater,
            renderer=renderer,
        )

        print_styled(
            f"Successfully bootstrapped {project_root} into a Flexlate project based off the template from {template.template_source_path}",
            SUCCESS_STYLE,
        )
