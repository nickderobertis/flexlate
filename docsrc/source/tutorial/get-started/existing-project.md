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
