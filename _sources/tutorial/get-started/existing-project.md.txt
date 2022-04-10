# Add Flexlate to a Project Already Generated from a Template

This guide covers taking
 a project that was previously generated from a template using
`cookiecutter` or `copier` and hooking it up with Flexlate to enable updating.

If you want to create a new project with Flexlate, you should follow 
the [new project](new-project.md) guide.
If you want to use Flexlate to add new templates within an existing 
project that was not generated from `cookiecutter` or `copier`, you 
should follow the [add to project guide](add-to-project.md).

## `fxt bootstrap`

The [`fxt bootstrap`](../../commands.md#fxt-bootstrap) command is used
to bootstrap a project that was previously generated from a template
so that it can be used with Flexlate. 

```{run-git-terminal}
---
setup: "copier https://github.com/nickderobertis/copier-simple-example.git . --data question1='my answer' --data question2='10' && git add -A && git commit -m 'Add template files without Flexlate'"
input: "[None,'my answer\\n10']"
---
ls
fxt bootstrap https://github.com/nickderobertis/copier-simple-example
ls
```

We can see that it prompts based on the questions in the template, be 
sure to enter these exactly as they are in your project to avoid 
unnecessary merge conflicts.

If your project is not already at the newest version of the template,
you can add the `--version` option to pass a specific version.

```shell
fxt bootstrap https://github.com/nickderobertis/copier-simple-example --version c7e1ba1bfb141e9c577e7c21ee4a5d3ae5dde04d
```

See the [command reference](../../commands.md#fxt-bootstrap) for full details.

## Next Steps

See how to [update your projct](../updating.md) to a newer template version. 