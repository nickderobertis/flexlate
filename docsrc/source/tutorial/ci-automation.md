# Automating Flexlate Workflows using CI

Flexlate comes with official Github Actions and workflows to automate
template updates using CI. This tutorial will walk you through the
process of setting up the workflows to update the templates and 
keep the [Flexlate branches](../core-concepts.md#branches-for-flexlate-operations) 
up to date.

By the end of this tutorial, template updates will be fully automated
in your project, besides approving PRs and resolving merge conflicts.

## Setting Up the Github Actions Workflows

### Option 1: Use the Official Copier Template

There is an [official Copier template](https://github.com/nickderobertis/copier-flexlate-github-actions) 
that contains the necessary workflows
to update the templates and keep the branches up to date. You can 
simply add it to your project and it should work as-is.

```{run-fxt-terminal}
---
input: "[None,'main']"
---
fxt add source https://github.com/nickderobertis/copier-flexlate-github-actions
fxt add output copier-flexlate-github-actions
ls -l .github/workflows
```

### Option 2: Manually add the Workflows

You can also just manually create the necessary workflow files in your 
project. The workflow files should be created in the `.github/workflows` directory.

#### Set up the Flexlate Update Workflow

Set up the [Flexlate Update action](https://github.com/nickderobertis/flexlate-update-action) 
to run on a schedule, or with 
a manual trigger:

```{rli} https://raw.githubusercontent.com/nickderobertis/flexlate-github-actions-example/main/.github/workflows/flexlate-update.yml
---
language: yaml
---
```

Both `actions/checkout` and `actions/setup-python` must be run
before the Flexlate Update Action. `actions/checkout` must be 
run with `fetch-depth: 0` so that all branches and history 
are fetched.

#### Set up the Flexlate After-Merge Workflow

Set up the [Flexlate After-Merge action](https://github.com/nickderobertis/flexlate-merge-action) 
to run after the main branch 
or a flexlate-output branch is merged:

```{rli} https://raw.githubusercontent.com/nickderobertis/flexlate-github-actions-example/main/.github/workflows/flexlate-after-merge.yml
---
language: yaml
---
```

`actions/checkout` must be run
before the Flexlate Update Action with `fetch-depth: 0` 
so that all branches and history are fetched. The remaining 
logic allows running the workflow manually targeting a specific 
set of Flexlate feature branches. 

## The Workflows, Explained

### Flexlate Update Workflow

This workflow uses the Flexlate Update Action to create PRs with template
updates. The workflow will run on a schedule or by manual trigger:

```{image} /_static/images/flexlate-update-workflow-run.png
---
alt: Flexlate Update Workflow Run
---
```

If there are no template updates, it will exit successfully. 

#### Update without Conflicts 

If there
are updates, then it will open a PR:

```{image} /_static/images/flexlate-pr-opened.png
---
alt: Flexlate PR Was Opened
---
```

You will see the new changes from the template as well as the version
in `flexlate.json` being updated.

```{image} /_static/images/flexlate-pr-diff.png
---
alt: Diff of the Flexlate Update PR
---
```

After you merge this PR, the Flexlate After-Merge workflow
will be triggered.

#### Update with Merge Conflicts

If there are merge conflicts, it will instead open a merge conflict 
resolution PR instead. 

```{image} /_static/images/flexlate-conflict-pr-opened.png
---
alt: Flexlate Merge Conflict Resolution PR Was Opened
---
```

You can resolve these conflicts right in Github's web editor:

```{image} /_static/images/flexlate-conflict-pr-highlight-web-editor.png
---
alt: The button within the Github PR to resolve merge conflicts
---
```

Clicking that button will take you into the web editor:

```{image} /_static/images/github-web-editor.png
---
alt: The Github UI to resolve merge conflicts
---
```

After you've resolved the conflicts, you should merge immediately. 
The merge to the main branch will
be in another step triggered by the Flexlate After-Merge workflow.

### Flexlate After-Merge Workflow

The after-merge workflow serves two functions: to merge Flexlate 
feature branches into Flexlate main branches, and to open a PR 
with template updates after resolving merge conflicts in the web
editor.

#### Merging Flexlate Feature Branches

After you've merged a feature branch that has corresponding Flexlate 
feature branches into the main branch, the after-merge workflow will
automatically merge those Flexlate feature branches into the Flexlate
main branches. 

```{image} /_static/images/flexlate-after-merge-workflow-run.png
---
alt: Flexlate After-Merge Workflow Run
---
```

```{image} /_static/images/git-tree-after-merge-flexlate-branches.png
---
alt: The state of the Git history after merging Flexlate feature branches into Flexlate main branches
---
```

#### Opening a PR with Template Updates After Conflict Resolution

After you've resolved merge conflicts in the web editor, the after-merge
workflow will run. It will see that a `flexlate-templates-*-for-conflicts`
branch was updated and automatically merge that branch into the original 
`flexlate-templates-` feature branch, then merge that branch into the 
feature branch. Then a PR will be opened with that feature branch. 
At the end of this process, it is just like a PR was opened in the 
first place without conflicts. 

```{image} /_static/images/git-tree-after-conflict-resolution.png
---
alt: The state of the Git history after resolving conflicts and opening a new PR
---
```