# Installing Flexlate

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

Before using Flexlate, you will also need to have 
[Git installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). 

## Next Steps

There are multiple ways to get started with Flexlate, depending on your 
project situation and goals. Pick the guide that best fits your situation,
then move on to the other concepts in the [user guide](../index.md).

- If you want to create a new project with Flexlate, you should follow 
the [new project](new-project.md) guide.
- If you already
have a project that was previously generated from a template using
`cookiecutter` or `copier` and you want to update it with Flexlate, 
you should follow the [existing project guide](existing-project.md). 
- If you want to use Flexlate to add new templates within an existing 
project that was not generated from `cookiecutter` or `copier`, you 
should follow the [add to project guide](add-to-project.md).
