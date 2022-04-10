# Flexlate Core Concepts

This guide introduces the core concepts of Flexlate. Read it to understand
how Flexlate works.

## Template Sources and Outputs

Flexlate has a concept of **template sources** and **applied templates**.
In order to apply a template, it must be first added as a template source.
Some commands will add the source at the same time as the applied output 
([`fxt init-from`](commands.md#fxt-init-from) and 
[`fxt bootstrap`](commands.md#fxt-bootstrap)), but otherwise you must 
first [add the template source](tutorial/get-started/add-to-project.md#add-the-template-source) 
and then 
[add the applied template](tutorial/get-started/add-to-project.md#add-template-output-s).

Flexlate was designed with this two-stage process so to support the use 
case of applying the same template source to multiple outputs with ease.
Once you register your template source with 
[`fxt add source`](commands.md#fxt-add-source), you can then refer to it 
only by its name rather than the full URL. You can also set a custom name
in case you'd like something shorter.

Template sources can be both local and remote. You could pass a path to 
a template within your current project, or use a Git url anywhere.

### Flexlate is Not a Template Engine

Flexlate itself does not render files. It wraps external project template 
engines to do the work. Currently, [`cookiecutter`](https://github.com/cookiecutter/cookiecutter) 
and [`copier`](https://github.com/copier-org/copier) are supported. There 
are future plans for additional template engines as well as an easier way 
to bring your own template engine to Flexlate.

## Git-Native

Flexlate is built upon [Git](https://git-scm.com/). Your project must be 
a Git repository for it to work, though the 
[`fxt init-from`](commands.md#fxt-init-from) 
command will create a new Git repository for you.

Why build Flexlate on Git? By using Git, while 
[updating your templates](tutorial/updating.md), if you encounter conflicts
they will be **real Git merge conflicts** that you can resolve with your
favorite merge tool. You will also not need to resolve the same conflicts 
again because Flexlate saves the state of your project in Git branches.

### Real Merge Conflicts

When you [update your templates](tutorial/updating.md), if you have changed
lines in the project that are also changed in the template source, you will 
encounter merge conflicts. These are real Git merge conflicts that can
be resolved with your favorite merge tool, such as 
[VS Code](https://code.visualstudio.com/docs/editor/versioncontrol#_merge-conflicts) 
or [GitKraken](https://www.gitkraken.com/blog/merge-conflict-tool).

When you encounter merge conflicts during a Flexlate operation, 
it will prompt you to resolve the conflicts, with an option to abort the
operation. Once you have resolved the conflicts, answer `y` to continue
and it will finish the Flexlate operation.

### Branches for Flexlate Operations

Flexlate stores the history of merge conflict resolutions in Git branches,
so that you won't have to resolve the same conflicts again. While Flexlate
tries to manage these branches for you as much as possible, you should be 
aware of their existence and will need to [run some simple commands to 
manage them](tutorial/saving.md). 

#### Flexlate Main Branches

Flexlate has two main branches that it uses to store the history of 
your merge conflict resolutions: the `flexlate-templates` and 
`flexlate-output` branches. The `flexlate-templates` branch stores 
only the output from your templates, not any of your other project files. 
The `flexlate-output` branch takes your current project and merges the 
`flexlate-templates` branch into it to keep it up to date with the templates, 
before merging back into your feature or main branch. 

#### Flexlate Feature Branches

To enable multiple people using Flexlate on the same project and 
to help [undo mistakes](tutorial/undoing.md), Flexlate creates feature 
versions of its branches corresponding to your currently checked out branch. 
For example if you are on a branch `my-feature`, when you do Flexlate operations
on the branch `my-feature`, it will create the branches `flexlate-templates-my-feature`
and `flexlate-output-my-feature` that are branched off the `flexlate-templates`
and `flexlate-output` branches, respectively. It will also automatically
pull `flexlate-templates` and `flexlate-output` before doing so in case your 
local branches are out of date.

#### Merging the Flexlate Feature Branches

Once you've finished with your Flexlate operations such as 
[updating](tutorial/updating.md), the new changes will be stored in the 
Flexlate feature branches rather than the main branches. Follow the 
[guide on saving](tutorial/saving.md) 
to understand the best way to merge the feature branches
into the main branches depending on your workflow.

## CI Workflows

Flexlate really shines when you can automate it with Github Actions.
It comes with official Github Actions to help you do so:
- The 
[Flexlate Update Action](https://github.com/nickderobertis/flexlate-update-action) 
can be used to help 
[automatically get PRs for template updates](tutorial/updating.md#get-automated-prs-with-template-updates).
- The
[Flexlate Merge Action](https://github.com/nickderobertis/flexlate-merge-action) 
can be used to 
[automate merging the Flexlate feature branches into the Flexlate main branches](tutorial/saving.md#merge-flexlate-branches-automatically-with-github-actions).

When you use these actions together, you can automate the whole process
of updating your templates, besides the one part that requires human 
intervention: resolving merge conflicts.

```{note}
You can see an example of 
[these workflows being used togehter](https://github.com/nickderobertis/flexlate/tree/master/.github/workflows)
in the 
[Flexate project itself](https://github.com/nickderobertis/flexlate).

See example workflow runs of the 
[Flexlate Update Action](https://github.com/nickderobertis/flexlate/actions/workflows/template-update.yml) 
and the
[merge action](https://github.com/nickderobertis/flexlate/actions/workflows/merge-flexlate.yml).
```

## Flexlate Configuration Files

### Project and User Configuration

Flexlate is configured on a project-by-project basis. The project configuration
can either live within the project, or within the user directory. It is 
useful to keep the project configuration in the user directory if it is 
a team project and the team has not bought into Flexlate yet. That way you
can still personally use Flexlate with the repo.

To store configuration in the user directory, you can use the `--user` flag
for [`fxt init`](commands.md#fxt-init) and use the user add mode for 
adding template sources and applied templates.

### `flexlate.json`

The `flexlate.json` files are plain JSON files that contain the configuration
of template sources and applied templates. The location of the `flexlate.json`
file will depend on the add mode. Here's an example of a `flexlate.json` file:

```json
{
  "template_sources": [
    {
      "name": "one",
      "path": "../input_files/templates/cookiecutters/one",
      "type": "cookiecutter",
      "version": "d512c7e14e83cb4bc8d4e5ae06bb357e",
      "git_url": null,
      "target_version": null,
      "render_relative_root_in_output": "{{ cookiecutter.a }}",
      "render_relative_root_in_template": "{{ cookiecutter.a }}"
    }
  ],
  "applied_templates": [
    {
      "name": "one",
      "data": {
        "a": "b",
        "c": ""
      },
      "version": "d512c7e14e83cb4bc8d4e5ae06bb357e",
      "add_mode": "local",
      "root": "."
    }
  ]
}
```

You can see it stores both details of the template source such as the current
version and the source path, but also the details of the applied templates, 
such as the location of the output and the data that was passed to the template.

Generally these files are generated and modified by Flexlate and you don't 
need to worry about them. If you want to make a manual config 
to a configuration file, you can follow the 
[guide for arbitrary changes](tutorial/arbitrary-changes.md).

### `flexlate-project.json`

Flexlate also has a single configuration file for the project itself.
It stores the root of the project as well as options that should be 
used for all Flexlate commands in the project.
Here's an example of `flexlate-project.json`:

```json
{
  "projects": [
    {
      "path": ".",
      "default_add_mode": "local",
      "merged_branch_name": "flexlate-output",
      "template_branch_name": "flexlate-templates",
      "remote": "origin"
    }
  ]
}
```

You can see that it stores the name of the remote and Flexlate branches, 
as well as the default add mode. It has this structure to support multiple 
projects in the user config.

This configuration file is automatically 
created with [`fxt init`](commands.md#fxt-init), 
[`fxt init-from`](commands.md#fxt-init-from), and
[`fxt bootstrap`](commands.md#fxt-bootstrap), but if you want to modify 
it after the fact, you can follow the 
[guide for arbitrary changes](tutorial/arbitrary-changes.md).

## Add Mode

Flexlate has a concept of an **add mode**, that represents where the 
`flexlate.json` configuration file should be created.

Flexlate supports three add modes:
- `local`: The template source or applied template `flexlate.json` is added at the root of the output.
- `project`: The template source or applied template `flexlate.json` is added at the project root.
- `user`: The template source or applied template `flexlate.json` is added to the user configuration file.

`local` is the default add mode. It is recommended because it becomes easy to
see whether files in a project are connected to Flexlate, because there 
will be a `flexlate.json` file in the folder with the applied template.
The `project` add mode is useful if you want to have all your Flexlate 
configuration in a single file instead. The `user` add mode is useful for 
when you are using Flexlate on a team project but your team has not 
bought into the tool yet, allowing you to apply and update templates in 
the project without anyone knowing you are using Flexlate.

When initializing the project with [`fxt init`](commands.md#fxt-init), 
[`fxt init-from`](commands.md#fxt-init-from), and
[`fxt bootstrap`](commands.md#fxt-bootstrap), you can pass the `--add-mode` flag to specify 
the default add mode. If you want to modify 
it after the fact, you can follow the 
[guide for arbitrary changes](tutorial/arbitrary-changes.md). You can also 
pass the `--add-mode` flag to any of the other commands to override 
the default add mode.

