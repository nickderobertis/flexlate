# Create a New Project with Flexlate

This guide covers creating a new project with Flexlate. If you already
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
fxt init-from https://github.com/nickderobertis/copier-simple-example --no-input
```

