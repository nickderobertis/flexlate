[![](https://codecov.io/gh/nickderobertis/flexlate/branch/master/graph/badge.svg)](https://codecov.io/gh/nickderobertis/flexlate)

#  flexlate

## Overview

Flexlate is a composable, maintainable system for managing templates.

### Features

- Update existing template outputs after there are changes to the template
  - When there is a conflict, it creates a git merge conflict so that you can
    resolve it with your favorite tooling
  - It keeps a history of the conflict resolution so you are not resolving 
    the same conflicts repeatedly
  - Use pre-built Github Actions to automatically get a PR in your project after 
    the template has been updated
- Compose a project with multiple templates
  - Add template sources and then you can apply outputs anywhere with a simple 
    CLI command
- Use your existing templates: both [`cookiecutter`](https://github.com/cookiecutter/cookiecutter) 
  and [`copier`](https://github.com/copier-org/copier) templates are supported
  - Works with both local and remote templates. You can even keep a template 
    in your project and be able to update outputs whenever it changes
- Apply it to your existing projects with a `bootstrap` functionality
- (planned) Use flexlate projects as templates themselves, enabling nested templates
  and sharing data across templates
- (planned) Allow multiple templates to coordinate on specific files in arbitrary 
  ways, e.g. think about applying a template and it adds its required packages 
  to `package.json` in a JS project

### Use Cases

- You want to create or already have projects that are generated from a `cookiecutter`
  or `copier` template, and keep those projects up to date with changes in the template
- You want to create a project from standard building blocks that can also be 
  updated systematically. For example think of something like a React component 
  with tests, a Java class and tests, or any set of files you want to generate

### Locally or Remote With a Team

In either case, you can use Flexlate 100% locally even on a team project 
without anyone else knowing you are using it via the `user` mode.

But Flexlate really shines when you embrace it fully and include it in
your remote repo. This enables you use CI to automatically open PRs with 
template updates.

### Why Flexlate?

Flexlate is born out of frustration with using project templates. 
You generate your project from a template, but later update the template 
and need to bring the changes back to your project. There are only a 
few tools for this and they do not have a great developer experience. 
Flexlate is Git-native, so you resolve template conflicts in Git as you would any 
other merge conflicts. 

Further, there is not really any ability to compose a project template from 
smaller templates with any existing tools.

### How does it Work?

Flexlate is Git-native: it carries out all its operations via commits to 
Git branches. It maintains two branches, one that contains the history of 
the template output and the other than contains the merged output between
your project and the template. This means that you resolve any conflicts 
with the template changes in Git and the merge conflict resolution is stored 
in the output branch.

It enables composability by using config files to keep track of where 
multiple templates should be rendered and with what data.

## Getting Started

### Installing

Flexlate is a Python package that includes the `fxt` command line utility. 
If you do not have Python, you will need to [install it](https://www.python.org/downloads/) 
first (required version is `>=3.8`).

The recommended way to install Flexlate is with [`pipx`](https://github.com/pypa/pipx),
though it can also be installed with `pip`.

```
pipx install flexlate
```

Or, if you don't have/don't want to install `pipx`:

```
pip install flexlate
```

### First Steps

#### New Project from a Template

To generate a new project from a template, use `init-from`, e.g.:

```shell
fxt init-from https://github.com/nickderobertis/copier-pypi-sphinx-flexlate
```
#### Existing Project from a Template

To add Flexlate to your project that is already generated from a `cookiecutter`
or `cruft` template, use `bootstrap`, e.g.:

```shell
fxt bootstrap https://github.com/nickderobertis/copier-pypi-sphinx-flexlate
```

#### Compose a Project from Multiple Templates

You can add a template source and then add as many outputs from that source 
as you want. 

Before you can do this, you must initialize a Flexlate project:

```shell
fxt init
```

Then you can add the template source:

```shell
fxt add source https://github.com/nickderobertis/copier-pypi-sphinx-flexlate
```

Then you can apply the output anywhere in the project:

```shell
fxt add output copier-pypi-sphinx-flexlate
```

### Updating a Template

#### Re-prompt Questions

Once you have updates in the template that you want to bring to your project,
run:

```shell
fxt update
```

This will prompt for all the questions again, using your previous answers 
as defaults. If there are new questions from the update, or if you want 
to change any of the answers, you should follow this flow. 

#### No Question Prompts

If instead you 
know that there are only changes in the outputs and not questions/answers, 
you can pass `--no-input` or `-n` to skip the questions:

```shell
fxt update -n
```

#### Saving your Work

##### Local Repo Flows

If you are following a local repo flow, then you can use the `fxt merge` command 
to merge the Flexlate feature branches into the Flexlate main branches. If 
you are using a feature-branch flow, then you would want to run `fxt merge` just 
before merging your feature branch into the main branch. If you are simply 
commititng to the main branch, just run `fxt merge` after any Flexlate command.

##### Remote Repo/PR Flows

If you are merging PRs in your repo rather than following a local flow, then 
you will want to `fxt push` just before/after your push your feature branch 
and open a PR. If you use the official Flexlate Github Merge Action, 
the Flexlate branches will be merged automatically after the PR is merged.

### Get Help

You can run `--help` on the end of any command to see documentation.

```shell
$ fxt --help
Usage: fxt [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  add        Add template sources and generate new projects and files...
  bootstrap  Takes an existing project that was already generated by...
  check      Checks whether there are any updates available for the...
  config     Modify Flexlate configs via CLI
  init       Initializes a flexlate project.
  init-from  Generates a project from a template and sets it up as a...
  merge      Merges feature flexlate branches into the main flexlate...
  push       Push flexlate branches to remote repositories
  remove     Remove template sources and previously generated outputs
  sync       Syncs manual changes to the flexlate branches, and updates...
  undo       Undoes the last flexlate operation, like ctrl/cmd + z for...
  update     Updates applied templates in the project to the newest...

```

Please raise an issue if anything is confusing or does not work properly.

See a
[more in-depth tutorial here.](
https://nickderobertis.github.io/flexlate/tutorial.html
)

## Development Status

This project is currently in early-stage development. There may be
breaking changes often. While the major version is 0, minor version
upgrades will often have breaking changes.

## Author

Created by Nick DeRobertis. MIT License.

## Links

See the
[documentation here.](
https://nickderobertis.github.io/flexlate/
)
