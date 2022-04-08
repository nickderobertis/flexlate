Search.setIndex({docnames:["api/flexlate","api/flexlate.finder","api/flexlate.finder.specific","api/flexlate.render","api/flexlate.render.specific","api/flexlate.template","api/flexlate.template_config","api/flexlate.transactions","api/flexlate.update","api/modules","auto_examples/index","commands","index","tutorial"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":5,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.todo":2,"sphinx.ext.viewcode":1,sphinx:56},filenames:["api/flexlate.rst","api/flexlate.finder.rst","api/flexlate.finder.specific.rst","api/flexlate.render.rst","api/flexlate.render.specific.rst","api/flexlate.template.rst","api/flexlate.template_config.rst","api/flexlate.transactions.rst","api/flexlate.update.rst","api/modules.rst","auto_examples/index.rst","commands.md","index.md","tutorial.rst"],objects:{"":[[0,0,0,"-","flexlate"]],"flexlate.add_mode":[[0,1,1,"","AddMode"],[0,3,1,"","get_expanded_out_root"]],"flexlate.add_mode.AddMode":[[0,2,1,"","LOCAL"],[0,2,1,"","PROJECT"],[0,2,1,"","USER"]],"flexlate.adder":[[0,1,1,"","Adder"]],"flexlate.adder.Adder":[[0,4,1,"","add_template_source"],[0,4,1,"","apply_template_and_add"],[0,4,1,"","init_project_and_add_to_branches"],[0,4,1,"","init_project_from_template_source_path"]],"flexlate.bootstrapper":[[0,1,1,"","Bootstrapper"]],"flexlate.bootstrapper.Bootstrapper":[[0,4,1,"","bootstrap_flexlate_init_from_existing_template"]],"flexlate.branch_update":[[0,3,1,"","abort_merge_and_reset_flexlate_branches"],[0,3,1,"","get_flexlate_branch_name"],[0,3,1,"","get_flexlate_branch_name_for_feature_branch"],[0,3,1,"","modify_files_via_branches_and_temp_repo"],[0,3,1,"","prompt_to_fix_conflicts_and_reset_on_abort_return_aborted"],[0,3,1,"","undo_transaction_in_flexlate_branches"]],"flexlate.checker":[[0,1,1,"","CheckResult"],[0,1,1,"","CheckResults"],[0,1,1,"","CheckResultsRenderable"],[0,1,1,"","Checker"]],"flexlate.checker.CheckResult":[[0,2,1,"","existing_version"],[0,5,1,"","has_update"],[0,2,1,"","latest_version"],[0,2,1,"","source_name"]],"flexlate.checker.CheckResults":[[0,5,1,"","has_updates"],[0,2,1,"","results"],[0,5,1,"","update_version_dict"],[0,5,1,"","updates"]],"flexlate.checker.CheckResultsRenderable":[[0,2,1,"","results"]],"flexlate.checker.Checker":[[0,4,1,"","find_new_versions_for_template_sources"]],"flexlate.cli":[[0,3,1,"","add_source"],[0,3,1,"","bootstrap"],[0,3,1,"","check"],[0,3,1,"","generate_applied_template"],[0,3,1,"","init_project"],[0,3,1,"","init_project_from"],[0,3,1,"","merge"],[0,3,1,"","pre_execute"],[0,3,1,"","push_feature"],[0,3,1,"","push_main"],[0,3,1,"","remove_template_output"],[0,3,1,"","remove_template_source"],[0,3,1,"","sync"],[0,3,1,"","undo"],[0,3,1,"","update_template_source_target_version"],[0,3,1,"","update_templates"]],"flexlate.cli_utils":[[0,3,1,"","confirm_user"]],"flexlate.config":[[0,1,1,"","AppliedTemplateConfig"],[0,1,1,"","AppliedTemplateWithSource"],[0,1,1,"","FlexlateConfig"],[0,1,1,"","FlexlateProjectConfig"],[0,1,1,"","ProjectConfig"],[0,1,1,"","TemplateSource"],[0,1,1,"","TemplateSourceWithTemplates"]],"flexlate.config.AppliedTemplateConfig":[[0,4,1,"","__init__"],[0,2,1,"","add_mode"],[0,2,1,"","data"],[0,2,1,"","name"],[0,2,1,"","root"],[0,2,1,"","version"]],"flexlate.config.AppliedTemplateWithSource":[[0,2,1,"","applied_template"],[0,2,1,"","source"],[0,4,1,"","to_template_and_data"]],"flexlate.config.FlexlateConfig":[[0,1,1,"","Config"],[0,2,1,"","applied_templates"],[0,5,1,"","child_configs"],[0,5,1,"","empty"],[0,4,1,"","from_dir_including_nested"],[0,4,1,"","from_multiple"],[0,4,1,"","load"],[0,4,1,"","save"],[0,4,1,"","template_name_must_be_unique"],[0,2,1,"","template_sources"],[0,5,1,"","template_sources_dict"]],"flexlate.config.FlexlateConfig.Config":[[0,2,1,"","extra"]],"flexlate.config.FlexlateProjectConfig":[[0,4,1,"","get_project_for_path"],[0,2,1,"","projects"]],"flexlate.config.ProjectConfig":[[0,2,1,"","default_add_mode"],[0,2,1,"","merged_branch_name"],[0,2,1,"","path"],[0,2,1,"","remote"],[0,2,1,"","template_branch_name"]],"flexlate.config.TemplateSource":[[0,5,1,"","absolute_local_path"],[0,4,1,"","from_template"],[0,2,1,"","git_url"],[0,5,1,"","is_local_template"],[0,2,1,"","name"],[0,2,1,"","path"],[0,2,1,"","render_relative_root_in_output"],[0,2,1,"","render_relative_root_in_template"],[0,2,1,"","target_version"],[0,4,1,"","to_template"],[0,2,1,"","type"],[0,5,1,"","update_location"],[0,2,1,"","version"]],"flexlate.config.TemplateSourceWithTemplates":[[0,1,1,"","Config"],[0,2,1,"","source"],[0,2,1,"","templates"]],"flexlate.config.TemplateSourceWithTemplates.Config":[[0,2,1,"","arbitrary_types_allowed"]],"flexlate.config_manager":[[0,1,1,"","ConfigManager"],[0,3,1,"","determine_config_path_from_roots_and_add_mode"]],"flexlate.config_manager.ConfigManager":[[0,4,1,"","add_applied_template"],[0,4,1,"","add_project"],[0,4,1,"","add_template_source"],[0,4,1,"","get_all_renderables"],[0,4,1,"","get_all_templates"],[0,4,1,"","get_applied_templates_with_sources"],[0,4,1,"","get_data_for_updates"],[0,4,1,"","get_no_op_updates"],[0,4,1,"","get_num_applied_templates_in_child_config"],[0,4,1,"","get_renderables_for_updates"],[0,4,1,"","get_sources_with_templates"],[0,4,1,"","get_template_by_name"],[0,4,1,"","get_template_sources"],[0,4,1,"","load_config"],[0,4,1,"","load_project_config"],[0,4,1,"","load_projects_config"],[0,4,1,"","load_specific_projects_config"],[0,4,1,"","move_applied_template"],[0,4,1,"","move_local_applied_templates_if_necessary"],[0,4,1,"","move_template_source"],[0,4,1,"","remove_applied_template"],[0,4,1,"","remove_template_source"],[0,4,1,"","save_config"],[0,4,1,"","save_projects_config"],[0,4,1,"","template_source_exists"],[0,4,1,"","update_template_source_version"],[0,4,1,"","update_template_sources"],[0,4,1,"","update_templates"]],"flexlate.config_manager.ConfigManager.remove_applied_template.params":[[0,6,1,"","config_path"],[0,6,1,"","orig_project_root"],[0,6,1,"","out_root"],[0,6,1,"","project_root"],[0,6,1,"","template_name"]],"flexlate.error_handler":[[0,3,1,"","simple_output_for_exceptions"]],"flexlate.exc":[[0,7,1,"","CannotFindAppliedTemplateException"],[0,7,1,"","CannotFindClonedTemplateException"],[0,7,1,"","CannotFindCorrectMergeParentException"],[0,7,1,"","CannotFindMergeForTransactionException"],[0,7,1,"","CannotFindTemplateSourceException"],[0,7,1,"","CannotLoadConfigException"],[0,7,1,"","CannotParseCommitMessageFlexlateTransaction"],[0,7,1,"","CannotRemoveAppliedTemplateException"],[0,7,1,"","CannotRemoveConfigItemException"],[0,7,1,"","CannotRemoveTemplateSourceException"],[0,7,1,"","ExpectedMergeCommitException"],[0,7,1,"","FlexlateConfigException"],[0,7,1,"","FlexlateConfigFileNotExistsException"],[0,7,1,"","FlexlateException"],[0,7,1,"","FlexlateGitException"],[0,7,1,"","FlexlateProjectConfigFileNotExistsException"],[0,7,1,"","FlexlateSyncException"],[0,7,1,"","FlexlateTemplateException"],[0,7,1,"","FlexlateTransactionException"],[0,7,1,"","FlexlateUpdateException"],[0,7,1,"","GitRepoDirtyException"],[0,7,1,"","GitRepoHasNoCommitsException"],[0,7,1,"","InvalidNumberOfTransactionsException"],[0,7,1,"","InvalidTemplateClassException"],[0,7,1,"","InvalidTemplateDataException"],[0,7,1,"","InvalidTemplatePathException"],[0,7,1,"","InvalidTemplateTypeException"],[0,7,1,"","LastCommitWasNotByFlexlateException"],[0,7,1,"","MergeCommitIsNotMergingAFlexlateTransactionException"],[0,7,1,"","MergeConflictsAndAbortException"],[0,7,1,"","RendererNotFoundException"],[0,7,1,"","TemplateLookupException"],[0,7,1,"","TemplateNotRegisteredException"],[0,7,1,"","TemplateSourceWithNameAlreadyExistsException"],[0,7,1,"","TooFewTransactionsException"],[0,7,1,"","TransactionMismatchBetweenBranchesException"],[0,7,1,"","TriedToCommitButNoChangesException"],[0,7,1,"","UnnecessarySyncException"],[0,7,1,"","UserChangesWouldHaveBeenDeletedException"]],"flexlate.ext_git":[[0,3,1,"","abort_merge"],[0,3,1,"","assert_repo_is_in_clean_state"],[0,3,1,"","branch_exists"],[0,3,1,"","checked_out_template_branch"],[0,3,1,"","checkout_template_branch"],[0,3,1,"","checkout_version"],[0,3,1,"","clone_repo_at_version_get_repo_and_name"],[0,3,1,"","delete_all_tracked_files"],[0,3,1,"","delete_local_branch"],[0,3,1,"","fast_forward_branch_without_checkout"],[0,3,1,"","get_branch_sha"],[0,3,1,"","get_commits_between_two_commits"],[0,3,1,"","get_current_version"],[0,3,1,"","get_merge_conflict_diffs"],[0,3,1,"","get_repo_remote_name_from_repo"],[0,3,1,"","list_tracked_files"],[0,3,1,"","merge_branch_into_current"],[0,3,1,"","push_to_remote"],[0,3,1,"","repo_has_merge_conflicts"],[0,3,1,"","reset_branch_to_commit_without_checkout"],[0,3,1,"","reset_current_branch_to_commit"],[0,3,1,"","restore_initial_commit_files"],[0,3,1,"","stage_and_commit_all"],[0,3,1,"","temp_repo_that_pushes_to_branch"],[0,3,1,"","update_local_branches_from_remote_without_checkout"]],"flexlate.finder":[[1,0,0,"-","multi"],[2,0,0,"-","specific"]],"flexlate.finder.multi":[[1,1,1,"","MultiFinder"]],"flexlate.finder.multi.MultiFinder":[[1,4,1,"","find"]],"flexlate.finder.specific":[[2,0,0,"-","base"],[2,0,0,"-","cookiecutter"],[2,0,0,"-","copier"],[2,0,0,"-","git"]],"flexlate.finder.specific.base":[[2,1,1,"","TemplateFinder"]],"flexlate.finder.specific.base.TemplateFinder":[[2,4,1,"","__init__"],[2,4,1,"","find"],[2,4,1,"","get_config"],[2,4,1,"","matches_template_type"]],"flexlate.finder.specific.cookiecutter":[[2,1,1,"","CookiecutterFinder"]],"flexlate.finder.specific.cookiecutter.CookiecutterFinder":[[2,4,1,"","find"],[2,4,1,"","get_config"],[2,4,1,"","matches_template_type"]],"flexlate.finder.specific.copier":[[2,1,1,"","CopierFinder"],[2,1,1,"","DefaultData"]],"flexlate.finder.specific.copier.CopierFinder":[[2,4,1,"","find"],[2,4,1,"","get_config"],[2,4,1,"","matches_template_type"]],"flexlate.finder.specific.copier.DefaultData":[[2,2,1,"","default"]],"flexlate.finder.specific.git":[[2,3,1,"","get_git_url_from_source_path"],[2,3,1,"","get_version_from_source_path"]],"flexlate.get_version":[[0,3,1,"","get_flexlate_version"]],"flexlate.logger":[[0,1,1,"","LogLevel"],[0,1,1,"","LoggingConfig"]],"flexlate.logger.LogLevel":[[0,2,1,"","DEBUG"],[0,2,1,"","INFO"]],"flexlate.logger.LoggingConfig":[[0,1,1,"","Config"],[0,4,1,"","cast_log_level"],[0,2,1,"","level"]],"flexlate.logger.LoggingConfig.Config":[[0,2,1,"","env_prefix"]],"flexlate.main":[[0,1,1,"","Flexlate"]],"flexlate.main.Flexlate":[[0,4,1,"","__init__"],[0,4,1,"","add_template_source"],[0,4,1,"","apply_template_and_add"],[0,4,1,"","bootstrap_flexlate_init_from_existing_template"],[0,4,1,"","check"],[0,4,1,"","init_project"],[0,4,1,"","init_project_from"],[0,4,1,"","merge_flexlate_branches"],[0,4,1,"","push_feature_flexlate_branches"],[0,4,1,"","push_main_flexlate_branches"],[0,4,1,"","remove_applied_template_and_output"],[0,4,1,"","remove_template_source"],[0,4,1,"","sync"],[0,4,1,"","undo"],[0,4,1,"","update"],[0,4,1,"","update_template_source_target_version"]],"flexlate.merger":[[0,1,1,"","Merger"]],"flexlate.merger.Merger":[[0,4,1,"","merge_flexlate_branches"]],"flexlate.path_ops":[[0,3,1,"","change_directory_to"],[0,3,1,"","copy_flexlate_configs"],[0,3,1,"","location_relative_to_new_parent"],[0,3,1,"","make_absolute_path_from_possibly_relative_to_another_path"],[0,3,1,"","make_all_dirs"],[0,3,1,"","make_func_that_creates_cwd_and_out_root_before_running"]],"flexlate.pusher":[[0,1,1,"","Pusher"]],"flexlate.pusher.Pusher":[[0,4,1,"","push_feature_flexlate_branches"],[0,4,1,"","push_main_flexlate_branches"]],"flexlate.remover":[[0,1,1,"","Remover"]],"flexlate.remover.Remover":[[0,4,1,"","remove_applied_template_and_output"],[0,4,1,"","remove_template_source"]],"flexlate.render":[[3,0,0,"-","multi"],[3,0,0,"-","renderable"],[4,0,0,"-","specific"]],"flexlate.render.multi":[[3,1,1,"","MultiRenderer"]],"flexlate.render.multi.MultiRenderer":[[3,4,1,"","render"],[3,4,1,"","render_string"]],"flexlate.render.renderable":[[3,1,1,"","Renderable"]],"flexlate.render.renderable.Renderable":[[3,1,1,"","Config"],[3,2,1,"","data"],[3,4,1,"","from_applied_template_with_source"],[3,2,1,"","out_root"],[3,2,1,"","skip_prompts"],[3,2,1,"","template"]],"flexlate.render.renderable.Renderable.Config":[[3,2,1,"","arbitrary_types_allowed"]],"flexlate.render.specific":[[4,0,0,"-","base"],[4,0,0,"-","cookiecutter"],[4,0,0,"-","copier"]],"flexlate.render.specific.base":[[4,1,1,"","SpecificTemplateRenderer"]],"flexlate.render.specific.base.SpecificTemplateRenderer":[[4,4,1,"","__init__"],[4,4,1,"","render"],[4,4,1,"","render_string"]],"flexlate.render.specific.cookiecutter":[[4,1,1,"","CookiecutterRenderer"]],"flexlate.render.specific.cookiecutter.CookiecutterRenderer":[[4,4,1,"","render"],[4,4,1,"","render_string"]],"flexlate.render.specific.copier":[[4,1,1,"","CopierRenderer"]],"flexlate.render.specific.copier.CopierRenderer":[[4,4,1,"","render"],[4,4,1,"","render_string"]],"flexlate.styles":[[0,3,1,"","print_styled"],[0,3,1,"","styled"]],"flexlate.syncer":[[0,1,1,"","Syncer"]],"flexlate.syncer.Syncer":[[0,4,1,"","sync_local_changes_to_flexlate_branches"]],"flexlate.template":[[5,0,0,"-","base"],[5,0,0,"-","cookiecutter"],[5,0,0,"-","copier"],[5,0,0,"-","hashing"],[5,0,0,"-","types"]],"flexlate.template.base":[[5,1,1,"","Template"]],"flexlate.template.base.Template":[[5,4,1,"","__init__"],[5,5,1,"","default_name"],[5,5,1,"","folder_hash"]],"flexlate.template.cookiecutter":[[5,1,1,"","CookiecutterTemplate"]],"flexlate.template.cookiecutter.CookiecutterTemplate":[[5,4,1,"","__init__"]],"flexlate.template.copier":[[5,1,1,"","CopierTemplate"]],"flexlate.template.copier.CopierTemplate":[[5,4,1,"","__init__"]],"flexlate.template.hashing":[[5,3,1,"","md5_dir"],[5,3,1,"","md5_file"],[5,3,1,"","md5_update_from_dir"],[5,3,1,"","md5_update_from_file"]],"flexlate.template.types":[[5,1,1,"","TemplateType"]],"flexlate.template.types.TemplateType":[[5,2,1,"","BASE"],[5,2,1,"","COOKIECUTTER"],[5,2,1,"","COPIER"]],"flexlate.template_config":[[6,0,0,"-","base"],[6,0,0,"-","cookiecutter"],[6,0,0,"-","copier"]],"flexlate.template_config.base":[[6,1,1,"","TemplateConfig"]],"flexlate.template_config.base.TemplateConfig":[[6,4,1,"","__init__"]],"flexlate.template_config.cookiecutter":[[6,1,1,"","CookiecutterConfig"]],"flexlate.template_config.copier":[[6,1,1,"","CopierConfig"]],"flexlate.template_config.copier.CopierConfig":[[6,4,1,"","__init__"]],"flexlate.template_data":[[0,3,1,"","merge_data"]],"flexlate.template_path":[[0,3,1,"","get_local_repo_path_and_name_cloning_if_repo_url"],[0,3,1,"","is_local_template"],[0,3,1,"","is_repo_url"]],"flexlate.transactions":[[7,0,0,"-","transaction"],[7,0,0,"-","undoer"]],"flexlate.transactions.transaction":[[7,1,1,"","FlexlateTransaction"],[7,7,1,"","HitInitialCommit"],[7,7,1,"","HitMergeCommit"],[7,1,1,"","TransactionType"],[7,3,1,"","assert_has_at_least_n_transactions"],[7,3,1,"","assert_last_commit_was_in_a_flexlate_transaction"],[7,3,1,"","assert_that_all_commits_between_two_are_flexlate_transactions_or_merges"],[7,3,1,"","create_transaction_commit_message"],[7,3,1,"","find_earliest_commit_that_was_part_of_transaction"],[7,3,1,"","find_earliest_merge_commit_for_transaction"],[7,3,1,"","find_last_transaction_from_commit"],[7,3,1,"","reset_last_transaction"]],"flexlate.transactions.transaction.FlexlateTransaction":[[7,4,1,"","cast_data_into_sequence"],[7,5,1,"","commit_message"],[7,2,1,"","data"],[7,2,1,"","id"],[7,2,1,"","out_root"],[7,4,1,"","parse_commit_message"],[7,2,1,"","target"],[7,2,1,"","type"]],"flexlate.transactions.transaction.TransactionType":[[7,2,1,"","ADD_OUTPUT"],[7,2,1,"","ADD_SOURCE"],[7,2,1,"","ADD_SOURCE_AND_OUTPUT"],[7,2,1,"","BOOTSTRAP"],[7,2,1,"","REMOVE_OUTPUT"],[7,2,1,"","REMOVE_SOURCE"],[7,2,1,"","SYNC"],[7,2,1,"","UPDATE"],[7,2,1,"","UPDATE_TARGET_VERSION"]],"flexlate.transactions.undoer":[[7,1,1,"","Undoer"]],"flexlate.transactions.undoer.Undoer":[[7,4,1,"","undo_transaction"],[7,4,1,"","undo_transactions"]],"flexlate.update":[[8,0,0,"-","main"],[8,0,0,"-","template"]],"flexlate.update.main":[[8,1,1,"","Updater"]],"flexlate.update.main.Updater":[[8,4,1,"","get_updates_for_templates"],[8,4,1,"","update"],[8,4,1,"","update_passed_templates_to_target_versions"]],"flexlate.update.template":[[8,1,1,"","TemplateUpdate"],[8,3,1,"","data_from_template_updates"],[8,3,1,"","updates_with_updated_data"]],"flexlate.update.template.TemplateUpdate":[[8,1,1,"","Config"],[8,2,1,"","config_location"],[8,2,1,"","data"],[8,2,1,"","index"],[8,4,1,"","matches_renderable"],[8,2,1,"","template"],[8,4,1,"","to_applied_template"],[8,4,1,"","to_renderable"]],"flexlate.update.template.TemplateUpdate.Config":[[8,2,1,"","arbitrary_types_allowed"]],"flexlate.user_config_manager":[[0,1,1,"","UserConfigManager"]],"flexlate.user_config_manager.UserConfigManager":[[0,4,1,"","update_template_source_target_version"]],flexlate:[[0,0,0,"-","add_mode"],[0,0,0,"-","adder"],[0,0,0,"-","bootstrapper"],[0,0,0,"-","branch_update"],[0,0,0,"-","checker"],[0,0,0,"-","cli"],[0,0,0,"-","cli_utils"],[0,0,0,"-","config"],[0,0,0,"-","config_manager"],[0,0,0,"-","constants"],[0,0,0,"-","error_handler"],[0,0,0,"-","exc"],[0,0,0,"-","ext_git"],[1,0,0,"-","finder"],[0,0,0,"-","get_version"],[0,0,0,"-","logger"],[0,0,0,"-","main"],[0,0,0,"-","merger"],[0,0,0,"-","path_ops"],[0,0,0,"-","pusher"],[0,0,0,"-","remover"],[3,0,0,"-","render"],[0,0,0,"-","styles"],[0,0,0,"-","syncer"],[5,0,0,"-","template"],[6,0,0,"-","template_config"],[0,0,0,"-","template_data"],[0,0,0,"-","template_path"],[7,0,0,"-","transactions"],[0,0,0,"-","types"],[8,0,0,"-","update"],[0,0,0,"-","user_config_manager"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","attribute","Python attribute"],"3":["py","function","Python function"],"4":["py","method","Python method"],"5":["py","property","Python property"],"6":["py","parameter","Python parameter"],"7":["py","exception","Python exception"]},objtypes:{"0":"py:module","1":"py:class","2":"py:attribute","3":"py:function","4":"py:method","5":"py:property","6":"py:parameter","7":"py:exception"},terms:{"0":12,"1":[0,7,11],"100":12,"3":12,"8":12,"break":12,"class":[0,1,2,3,4,5,6,7,8,12],"default":[0,2,6,11,12],"do":[0,11,12],"enum":[0,5,7],"function":[0,12,13],"import":13,"int":8,"new":[0,11],"return":[0,1,2,3,4,5,7,8],"switch":0,"true":[0,3,8],"while":[11,12],A:[0,11],Be:[0,11],But:12,By:11,For:12,If:[0,11,12],In:12,It:[0,11,12],Or:12,The:[0,11,12],Then:12,There:12,To:12,__init__:[0,2,4,5,6],_env_fil:0,_env_file_encod:0,_env_nested_delimit:0,_secrets_dir:0,abc:[5,6],abil:12,abl:12,abort:11,abort_merg:0,abort_merge_and_reset_flexlate_branch:0,abort_on_conflict:[0,8],about:[0,12],absolute_local_path:0,abstractcontextmanag:0,accordingli:[0,11],across:12,action:12,add:[0,7,12],add_applied_templ:0,add_mod:9,add_output:7,add_project:0,add_sourc:[0,7],add_source_and_output:7,add_template_sourc:0,adder:9,additional_branch:0,addmod:0,adjust_applied_path:0,adjust_root:[0,8],after:[0,11,12],again:12,against:[0,11],all:[10,11,12],allow:[0,12],allow_conflict:0,alreadi:[0,11,12],also:[0,11,12],alwai:[0,11],an:[0,5,7,11,12],ani:[0,3,4,7,8,11,12],anoth:[0,11],answer:[11,12],anyon:12,anyth:12,anywher:12,appli:[0,11,12],applied_templ:0,applied_template_with_sourc:3,appliedtemplateconfig:[0,8],appliedtemplatewithsourc:0,apply_template_and_add:0,ar:[0,11,12],arbitrari:12,arbitrary_types_allow:[0,3,8],arg:[2,4,11,12],argument:[0,11],assert_has_at_least_n_transact:7,assert_last_commit_was_in_a_flexlate_transact:7,assert_repo_is_in_clean_st:0,assert_that_all_commits_between_two_are_flexlate_transactions_or_merg:7,auto_examples_jupyt:10,auto_examples_python:10,automat:[11,12],avail:[0,11,12],back:12,base:[0,1,3,7,8,9],base_branch:0,base_branch_nam:0,base_merged_branch_nam:[0,7,8],base_template_branch_nam:[0,7,8],baseconfig:0,basemodel:[0,3,7,8],baseset:0,bash:12,been:12,befor:[0,11,12],below:10,between:[11,12],block:12,bool:[0,2,3,8],bootstrap:[0,7,12],bootstrap_flexlate_init_from_existing_templ:0,bootstrapp:9,born:12,both:12,bound:2,branch:[0,11,12],branch_exist:0,branch_nam:[0,11],branch_upd:9,bring:12,build:12,built:12,can:[0,11,12],cannot:0,cannotfindappliedtemplateexcept:0,cannotfindclonedtemplateexcept:0,cannotfindcorrectmergeparentexcept:0,cannotfindmergefortransactionexcept:0,cannotfindtemplatesourceexcept:0,cannotloadconfigexcept:0,cannotparsecommitmessageflexlatetransact:0,cannotremoveappliedtemplateexcept:0,cannotremoveconfigitemexcept:0,cannotremovetemplatesourceexcept:0,care:0,carri:12,cast_data_into_sequ:7,cast_log_level:0,chang:[0,11,12],change_directory_to:0,check:[0,8,12],checked_out_template_branch:0,checker:9,checkout_template_branch:0,checkout_vers:0,checkresult:0,checkresultsrender:0,child_config:0,child_config_path:0,ci:[11,12],classmethod:[0,3,7],cli:[9,11,12],cli_util:9,clone_repo_at_version_get_repo_and_nam:0,cmd:[0,11,12],code:[0,10,11],com:12,combin:11,command:[0,11,12],commit:[0,7,11,12],commit_messag:[0,7],commit_sha:0,commititng:12,complet:[11,12],compon:12,compos:0,config:[3,5,8,9,12],config_loc:8,config_manag:[8,9],config_path:0,configmanag:[0,8],configur:11,confirm_us:0,conflict:[11,12],confus:12,constant:9,contain:12,conveni:[0,11],cookiecutt:[0,1,3,9,11,12],cookiecutterconfig:[2,6],cookiecutterfind:2,cookiecutterrender:4,cookiecuttertempl:[2,4,5],coordin:12,copi:[11,12],copier:[0,1,3,9,11,12],copierconfig:[2,6],copierfind:2,copierrender:4,copiertempl:[2,4,5],copy_current_config:0,copy_flexlate_config:0,correspond:[0,11],creat:[0,11,12],create_transaction_commit_messag:7,cruft:12,ctrl:[0,11,12],current:[0,11,12],current_branch:0,custom:[11,12],cwd:0,data:[0,3,7,8,12],data_from_template_upd:8,date:12,debug:0,default_add_mod:0,default_folder_nam:0,default_nam:5,defaultdata:2,delet:[0,11],delete_all_tracked_fil:0,delete_local_branch:0,delete_tracked_fil:0,depth:12,deroberti:12,determine_config_path_from_roots_and_add_mod:0,dict:[0,2,3,4,7,8],directori:[0,2,5,11],discard:[0,11],displai:[0,11],doe:[0,8],don:[11,12],download:10,dst:0,dst_folder:0,e:12,earli:12,easi:[0,11],either:12,els:12,embrac:12,empti:0,enabl:[11,12],encount:11,end:[0,7,12],enumer:[0,5,7],env_prefix:0,env_set:0,error_handl:9,even:[0,12],exampl:[10,13],exc:9,except:[0,7],exist:[0,11],existing_vers:0,exit:[11,12],expectedmergecommitexcept:0,experi:12,ext_git:9,extra:0,f:11,fals:[0,3,4,8,11],fast_forward_branch_without_checkout:0,favorit:12,featur:0,feature_branch:[0,11],few:12,ff_branch:0,file:[0,11,12],file_oper:0,filenam:5,find:[1,2],find_earliest_commit_that_was_part_of_transact:7,find_earliest_merge_commit_for_transact:7,find_last_transaction_from_commit:7,find_new_versions_for_template_sourc:0,finder:[0,8,9],fish:12,flexlat:11,flexlate_log_:0,flexlateconfig:0,flexlateconfigexcept:0,flexlateconfigfilenotexistsexcept:0,flexlateexcept:0,flexlategitexcept:0,flexlateprojectconfig:0,flexlateprojectconfigfilenotexistsexcept:0,flexlatesyncexcept:0,flexlatetemplateexcept:0,flexlatetransact:7,flexlatetransactionexcept:0,flexlateupdateexcept:0,folder:11,folder_hash:5,folder_nam:0,follow:12,force_push:0,form:0,from:0,from_applied_template_with_sourc:3,from_dir_including_nest:0,from_multipl:0,from_templ:0,frustrat:12,full_rerend:8,fulli:12,func:0,further:12,fxt:12,g:12,gener:[0,3,10,11,12],generate_applied_templ:0,get_all_render:0,get_all_templ:0,get_applied_templates_with_sourc:0,get_branch_sha:0,get_commits_between_two_commit:0,get_config:2,get_current_vers:0,get_data_for_upd:0,get_expanded_out_root:0,get_flexlate_branch_nam:0,get_flexlate_branch_name_for_feature_branch:0,get_flexlate_vers:0,get_git_url_from_source_path:2,get_local_repo_path_and_name_cloning_if_repo_url:0,get_merge_conflict_diff:0,get_no_op_upd:0,get_num_applied_templates_in_child_config:0,get_project_for_path:0,get_renderables_for_upd:0,get_repo_remote_name_from_repo:0,get_sources_with_templ:0,get_template_by_nam:0,get_template_sourc:0,get_updates_for_templ:8,get_vers:9,get_version_from_source_path:2,git:[0,1,11,12],git_url:[0,5],github:12,gitrepodirtyexcept:0,gitrepohasnocommitsexcept:0,given:[0,11],great:12,ha:[0,11,12],has_upd:0,hash:[0,9],have:12,help:11,here:12,higher:0,highlight:13,histori:[0,11,12],hitinitialcommit:7,hitmergecommit:7,http:12,id:7,includ:12,index:[8,12],info:0,inform:12,init:12,init_project:0,init_project_and_add_to_branch:0,init_project_from:0,init_project_from_template_source_path:0,initi:[0,11,12],input:[0,11,12],instal:11,instead:12,invalidnumberoftransactionsexcept:0,invalidtemplateclassexcept:0,invalidtemplatedataexcept:0,invalidtemplatepathexcept:0,invalidtemplatetypeexcept:0,is_local_templ:0,is_repo_url:0,issu:12,its:12,java:12,js:12,json:12,jupyt:10,just:12,keep:12,keyword:0,know:12,kwarg:[0,2,4],last:[0,11,12],lastcommitwasnotbyflexlateexcept:0,later:12,latest_vers:0,level:0,licens:12,like:[0,11,12],line:12,list:[0,3,8],list_tracked_fil:0,load:0,load_config:0,load_project_config:0,load_projects_config:0,load_specific_projects_config:0,local:[0,11],local_path:2,locat:[0,11],location_relative_to_new_par:0,logger:9,loggingconfig:0,logic:0,loglevel:0,longer:0,look:12,lower:0,mai:[0,11,12],main:[3,7,9,12],maintain:[0,12],major:12,make_absolute_path_from_possibly_relative_to_another_path:0,make_all_dir:0,make_func_that_creates_cwd_and_out_root_before_run:0,manag:[0,12],mani:12,manual:[0,11,12],match:11,matches_render:8,matches_template_typ:2,md5_dir:5,md5_file:5,md5_update_from_dir:5,md5_update_from_fil:5,mean:12,merg:[0,12],merge_branch_into_curr:0,merge_data:0,merge_flexlate_branch:0,mergecommitisnotmergingaflexlatetransactionexcept:0,mergeconflictsandabortexcept:0,merged_branch_nam:[0,7,8],merged_branch_sha:0,merger:9,messag:[0,7,11,12],minor:12,mit:12,mode:[11,12],model:0,modifi:[0,11,12],modify_files_via_branches_and_temp_repo:0,modul:[9,12],more:12,move:[0,11],move_applied_templ:0,move_local_applied_templates_if_necessari:0,move_template_sourc:0,multi:[0,8,9],multifind:[0,1,8],multirender:[0,3,8],must:[0,11,12],n:[7,11,12],name:[0,5,11],nativ:12,need:[0,11,12],nest:12,new_config_path:0,new_par:0,newest:[0,11,12],nick:12,nickderoberti:12,no_input:[0,3,4,8],none:[0,1,5,8],note:[0,8,11],notebook:10,num_oper:[0,11],num_transact:7,number:11,object:[0,1,3,7,8],offici:12,often:12,onc:12,one:12,onli:[0,11,12],open:12,oper:[0,11,12],option:[0,2,7,8,11,12],orig_par:0,orig_project_root:0,origin:[0,8,11],other:[0,11,12],out:12,out_root:[0,3,7],output:[0,7,8,12],overrid:0,overriden:5,p:11,packag:[9,12],page:12,paramet:0,pars:0,parse_commit_messag:7,pass:[0,11,12],path:[0,1,2,3,5,7,8,11],path_is_relative_to:0,path_op:9,pathlib:[0,3,7,8],pip:[12,13],pipx:12,plan:12,pleas:12,posixpath:[0,3,5,6,8],possibly_relative_to:0,powershel:12,pre:12,pre_execut:0,prevent:11,previou:12,previous:[11,12],print_styl:0,project:[0,11],project_path:0,project_root:[0,3,8],projectconfig:0,prompt:[0,11],prompt_to_fix_conflicts_and_reset_on_abort_return_abort:0,properli:12,properti:[0,5,7],protect:[0,11],protocol:[2,4],provid:[0,11],push:[0,12],push_featur:0,push_feature_flexlate_branch:0,push_main:0,push_main_flexlate_branch:0,push_to_remot:0,pusher:9,pwsh:12,pyappconf:0,pydant:[0,3,7,8],pypi:12,python:[10,12],q:11,quiet:[0,11],r:11,rais:[0,12],rather:[11,12],react:12,realli:12,recommend:12,refer:12,relative_to:0,remot:[0,8,11],remote_nam:0,remov:[7,9,12],remove_applied_templ:0,remove_applied_template_and_output:0,remove_output:7,remove_sourc:7,remove_template_output:0,remove_template_sourc:0,render:[0,8,9,11,12],render_relative_root:5,render_relative_root_in_output:[0,5],render_relative_root_in_templ:[0,5,6],render_root:8,render_str:[3,4],renderernotfoundexcept:0,repeatedli:12,repo:[0,7,8,11],repo_has_merge_conflict:0,repositori:[0,11,12],requir:[11,12],reset_branch_to_commit_without_checkout:0,reset_current_branch_to_commit:0,reset_last_transact:7,resolut:12,resolv:12,restore_initial_commit_fil:0,result:0,root:[0,11],run:[0,11,12],s:[0,11],same:[0,12],satisfi:[0,11],save:0,save_config:0,save_projects_config:0,script:[0,11],search:12,see:12,sequenc:7,serializer_kwarg:0,set:[0,11,12],sha:11,share:12,shell:[11,12],shine:12,should:[0,5,11,12],show:[11,12],similar:12,simpl:[12,13],simple_output_for_except:0,simpli:12,skip:12,skip_prompt:3,smaller:12,so:[0,11,12],some:13,someth:12,sourc:[0,1,2,3,4,5,6,7,8,10,12],source_nam:0,specif:[0,1,3,11,12],specifi:12,specifictemplaterender:4,sphinx:[10,12],src:0,stage:12,stage_and_commit_al:0,stai:0,standard:12,start:[0,7],still:[0,11],store:[0,11,12],str:[0,2,3,4,5,7,8],string:[3,4],style:9,submodul:9,subpackag:9,support:12,sure:[0,11],sync:[0,7,12],sync_local_changes_to_flexlate_branch:0,syncer:9,system:[0,11,12],systemat:12,t:[2,3,4,11,12],tabular:[0,11],take:[0,11,12],target:[0,7,12],target_vers:[0,5],temp:0,temp_repo_that_pushes_to_branch:0,templat:[0,1,2,3,4,7,9,11],template_branch_nam:[0,7,8],template_branch_sha:0,template_config:[0,9],template_data:9,template_kwarg:2,template_nam:[0,11],template_name_must_be_uniqu:0,template_path:[9,11],template_root:[0,11],template_sourc:0,template_source_exist:0,template_source_path:5,template_sources_dict:0,template_vers:0,templateconfig:[2,6],templatefind:2,templatelookupexcept:0,templatenotregisteredexcept:0,templatesourc:0,templatesourcewithnamealreadyexistsexcept:0,templatesourcewithtempl:0,templatetyp:[0,5],templateupd:[0,8],test:12,text:11,than:[11,12],thei:[0,11,12],themselv:12,thi:[0,11,12,13],think:12,those:[0,12],though:12,to_applied_templ:8,to_render:8,to_templ:0,to_template_and_data:0,toofewtransactionsexcept:0,tool:[0,11,12],track:12,transact:[0,8,9],transactionmismatchbetweenbranchesexcept:0,transactiontyp:7,triedtocommitbutnochangesexcept:0,tupl:0,two:12,type:[1,2,3,4,7,8,9],typer:0,typevar:2,undo:[0,12],undo_transact:7,undo_transaction_in_flexlate_branch:0,undoer:[0,9],union:0,unnecessarysyncexcept:0,until:[0,11],up:[0,11,12],updat:[0,7,9],update_loc:0,update_local_branches_from_remote_without_checkout:0,update_passed_templates_to_target_vers:8,update_target_vers:7,update_templ:0,update_template_sourc:0,update_template_source_target_vers:0,update_template_source_vers:0,update_version_dict:0,updates_with_updated_data:8,upgrad:12,url:[0,11],us:[0,11],usag:[11,12],use_template_source_path:0,user:[0,11,12],user_config_manag:9,userchangeswouldhavebeendeletedexcept:0,userconfigmanag:0,util:12,uuid4:7,v:[0,7,11],valid:0,validationerror:0,valu:[0,5,7],version:[0,1,5,7,11,12],via:[11,12,13],wa:[0,11,12],wai:[0,11,12],want:[0,11,12],we:11,what:12,when:[0,11,12],whenev:12,where:12,whether:[0,11,12],which:11,without:12,work:0,would:12,you:[0,11,12],your:[0,11],z:[0,11,12],zip:10,zsh:12},titles:["flexlate package","flexlate.finder package","flexlate.finder.specific package","flexlate.render package","flexlate.render.specific package","flexlate.template package","flexlate.template_config package","flexlate.transactions package","flexlate.update package","flexlate","This is my gallery","<code class=\"docutils literal notranslate\"><span class=\"pre\">fxt</span></code>","Welcome to Flexlate documentation!","Getting started with flexlate"],titleterms:{"case":12,"new":12,No:12,With:12,add:11,add_mod:0,adder:0,api:12,author:12,base:[2,4,5,6],bootstrap:11,bootstrapp:0,branch_upd:0,check:11,checker:0,cli:0,cli_util:0,compos:12,config:[0,11],config_manag:0,constant:0,cookiecutt:[2,4,5,6],copier:[2,4,5,6],develop:12,document:12,doe:12,error_handl:0,exampl:12,exc:0,exist:12,ext_git:0,featur:[11,12],finder:[1,2],first:12,flexlat:[0,1,2,3,4,5,6,7,8,9,12,13],flow:12,from:[11,12],fxt:11,galleri:10,get:[12,13],get_vers:0,git:2,hash:5,help:12,how:12,indic:12,init:11,instal:[12,13],link:12,local:12,logger:0,main:[0,8,11],merg:11,merger:0,modul:[0,1,2,3,4,5,6,7,8],multi:[1,3],multipl:12,my:10,output:11,overview:12,packag:[0,1,2,3,4,5,6,7,8],path_op:0,pr:12,project:12,prompt:12,push:11,pusher:0,question:12,re:12,remot:12,remov:[0,11],render:[3,4],repo:12,save:12,sourc:11,specif:[2,4],start:[12,13],statu:12,step:12,style:0,submodul:[0,1,2,3,4,5,6,7,8],subpackag:[0,1,3],sync:11,syncer:0,target:11,team:12,templat:[5,8,12],template_config:6,template_data:0,template_path:0,thi:10,transact:7,tutori:12,type:[0,5],undo:11,undoer:7,updat:[8,11,12],us:12,usag:13,user_config_manag:0,welcom:12,why:12,work:12,your:12}})