# Add New Templates within An Existing Project

This guide covers using Flexlate to add new templates within an existing 
project that was not generated from `cookiecutter` or `copier`.

If you already
have a project that was previously generated from a template using
`cookiecutter` or `copier` and you want to update it with Flexlate, 
you should follow the [existing project guide](existing-project.md). 
If you want to create a new project with Flexlate, you should follow 
the [new project](new-project.md) guide.

## Initialize the Flexlate Project

The [`fxt init`](../../commands.md#fxt-bootstrap) command is used
to initialize a new Flexlate project. You must have a Flexlate project 
before you can add any template sources or outputs.

```{run-git-terminal}
fxt init
```

## Add the Template Source

The [`fxt add source`](../../commands.md#fxt-add-source) command registers 
a template source in the Flexlate configuration file.

```{run-fxt-terminal}
fxt add source https://github.com/nickderobertis/copier-simple-example
cat flexlate.json
```

You can also specify the `--version` option to specify which version of 
the template you would like to be able to output.

```shell
fxt add source https://github.com/nickderobertis/copier-simple-example --version c7e1ba1bfb141e9c577e7c21ee4a5d3ae5dde04d
```

## Add Template Output(s)

The [`fxt add output`](../../commands.md#fxt-add-output) command renders the 
template at the specified location. 

```{run-fxt-terminal}
---
setup: "fxt add source https://github.com/nickderobertis/copier-simple-example"
input: "my answer\n10"
---
fxt add output copier-simple-example some/path
ls some/path
```

If you don't specify a path to render the template to, the template will be 
rendered in the current working directory.

```shell
fxt add output copier-simple-example
```

## Next Steps

See how to [update your project](../updating.md) to a newer template version.