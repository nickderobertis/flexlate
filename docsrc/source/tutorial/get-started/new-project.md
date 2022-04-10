# Create a New Project with Flexlate

This guide covers creating a new project with Flexlate. 

If you already
have a project that was previously generated from a template using
`cookiecutter` or `copier` and you want to update it with Flexlate, 
you should follow the [existing project guide](existing-project.md). 
If you want to use Flexlate to add new templates within an existing 
project that was not generated from `cookiecutter` or `copier`, you 
should follow the [add to project guide](add-to-project.md).

## `fxt init-from`

The [`fxt init-from`](../../commands.md#fxt-init-from) command is used to create 
a new Flexlate project from a template. It will also create a new folder 
and initialize a git repository in it before adding the Flexlate output.
Let's give it a try with a very minimal example template:

```{run-git-terminal}
---
input: "my answer\n10\nmy-project"
---
fxt init-from https://github.com/nickderobertis/copier-simple-example
cd my-project
ls
```

We can see that it prompts based on the questions in the template, and 
then for the name of the generated folder.

```{note}
Cookiecutter templates will not prompt for a folder name, it is 
already determined by the template questions.
```

We can see that it generated the project complete with a Flexlate 
project config and config for the applied template.

If you want to generate the project from a template at a specific version, 
`--version` can be used, for example:

```shell
fxt init-from --version c7e1ba1bfb141e9c577e7c21ee4a5d3ae5dde04d https://github.com/nickderobertis/copier-simple-example 
```

See the [command reference](../../commands.md#fxt-init-from) for full details.

## Next Steps

See how to [update your projct](../updating.md) to a newer template version.
