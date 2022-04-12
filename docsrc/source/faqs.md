# Frequently Asked Questions

## What is a Project or File Generator?

A project or file generator is a tool that generates a file, multiple files, or an
entire project from a template. The templates define questions to ask the user,
and the answers to the questions are used to generate the file(s) or project.

Let's look at an example of using [`copier`](https://github.com/copier-org/copier) to generate a project.

You can see the example 
[Copier template project here](https://github.com/nickderobertis/copier-simple-example).
It defines a `copier.yaml` that describes the questions that should be asked
of the user: 

```yaml
question1: answer1

question2:
  help: The second question
  type: float
  default: 2.7
```

In the files of the template, it has a `{{ question1 }}.txt.jinja` file that 
has the contents:

```
{{ question2 }}
some new footer
```

Let's see what it looks like to generate the file from this template.

```{warning}
When you use Flexlate, you don't need to run the underlying project generator 
tool: instead Flexlate wraps these tools so you only need to use Flexlate. So
don't follow this example, it is only for illustrative purposes. Instead 
look at 
[starting a new Flexlate project from a template](tutorial/get-started/new-project.md).
```

```{run-git-terminal}
---
input: "something\n100"
---
copier https://github.com/nickderobertis/copier-simple-example.git my-project
cd my-project
ls
cat something.txt
```

We can see that the project generator replaces template tags based on the answers 
provided in the prompts for both the file names and file contents.

A project generator when used within Flexlate is referred to as a **template engine**. 
The currently supported template engines are [`cookiecutter`](https://github.com/cookiecutter/cookiecutter) 
  and [`copier`](https://github.com/copier-org/copier).

Here is a list of some project generator tools you might be familiar with:
- [Cookiecutter](https://github.com/cookiecutter/cookiecutter)
- [Copier](https://github.com/copier-org/copier)
- [Yeoman](https://yeoman.io/)
- [Plop](https://github.com/plopjs/plop)
- [Hygen](https://github.com/jondot/hygen)
- [slush](https://github.com/slushjs/slush)
- [generate](https://github.com/generate/generate)
- [GENie](https://github.com/bkaradzic/GENie)
- [kickstart](https://github.com/Keats/kickstart)
- [yogini](https://github.com/raineorshine/yogini)
- [rendr](https://github.com/jamf/rendr)

```{note}
It is a planned feature to make it easier to add new template engines 
and allow the user to bring their own template engines. Please raise 
an [issue on Github](https://github.com/nickderobertis/flexlate/issues) 
if you'd like to see support for a particular template engine.
```

## Why Create Flexlate?

### Project Generator Pain

I, Nick DeRobertis, have 
[a lot of open source projects](https://nickderobertis.com/software), especially
Python packages hosted on PyPI. I was drawn to [project generators](#what-is-a-project-or-file-generator)
because they took all the boilerplate work out of creating a new project,
and often I just want to get hacking on something and the work to create the 
project would stop me or encourage me to not release it on PyPI.

#### Difficulty of Updates

As I scaled up my use of 
[project generators](#what-is-a-project-or-file-generator), 
I quickly realized that
there were improvements I wanted to make to the project template, but once 
I did so only the new projects I generate would have the improvements, 
not the old projects I've already generated and am still maintaining. It 
was a manual process to bring those updates back into the old projects.

I figured, this must be a solved problem, as anyone who uses 
[project generators](#what-is-a-project-or-file-generator) for more than 
a few projects over time will go through this pain. So I began searching
for a tool to use to update my projects with updates in the templates, 
but it's not the only problem I encountered.

#### Lack of Modularity

I have a variety of types of projects, some are in Python and some 
are in TypeScript or other languages, and even within Python I might 
be building a CLI tool, a web app, a desktop app, an AWS Lambda, etc.
Some projects may be full-stack, incorporating multiple of such projects within 
a mono-repo.
Some of these projects may be open-source and published to PyPI
and others for personal use. All of these types of projects have their 
own common requirements, but there are some of the same requirements across 
multiple types of projects. For example, I would like to share some CI 
pipelines across all my projects. I could create a project generator for 
each of these project types, but then it becomes difficult to manage the 
shared parts of these generators. 

Modern software development typically embraces modularity. Yet there 
has previously not been any way to combine multiple project generators 
meaningfully. I could not find any tools that attempt to solve this problem,
though I did find some that try to solve the updating problem.

### Existing Tools to Update Applied Templates

I began my search for tools that can update templates. At the time I was
using [`cookiecutter`](https://github.com/cookiecutter/cookiecutter) for 
my main template. I read this 
[Cookiecutter issue](https://github.com/cookiecutter/cookiecutter/issues/784)
that revealed many others are looking for the same functionality.
There is a [`milhoja`](https://github.com/rmedaer/milhoja) tool mentioned there
that does not seem well supported.

#### Cruft

This ultimately led me to finding
[`cruft`](https://github.com/cruft/cruft), which I used for more than 
a year to update my projects and is well-supported. The 
developer experience was OK, it would create markers in the files 
signifying the changes, very similar to Git merge conflicts, but not 
actual merge conflicts and so no standard tooling would work to resolve them.
At some point, this behavior changed, and now it produces separate `.rej`
and `.orig` files that need to be manually looked through and reworked
to resolve the conflicts. You need to see the conflict in the `.rej` file,
bring over the appropriate changes to the normal file, and delete the 
`.orig` file. No standard tooling
tooling will help with this process, and I was finding it very cumbersome 
to update my projects. I considered 
[modifying the `cruft` tool](https://github.com/cruft/cruft/issues/49#issuecomment-787942536) 
to regain the old experience, but even the old experience was not ideal 
as standard merge tools wouldn't work.

Further, Cruft is a tool designed to specifically work for Cookiecutter, 
but this problem is not specific to any 
[project generator](#what-is-a-project-or-file-generator). It also 
will only work with templates defined in Git repositories.

#### Copier

[`copier`](https://github.com/copier-org/copier) has its own 
[updating functionality](https://copier.readthedocs.io/en/stable/updating/) 
built-in. At the time, I was using Cookiecutter and so there was no way
to use this functionality to update my existing projects.

Copier's updating experience is very similar to [Cruft](#cruft).
It creates `.rej` files that need be be manually handled without any 
merge tooling. It also requires that the template is a Git repository.
It only works with Copier templates.

### Expanding the Scope

#### Ability to Use Standard Merge Tools

I thought there
should be a tool that can produce 
[real Git merge conflicts](core-concepts.md#real-merge-conflicts) so that 
all standard merge tools such as 
[VS Code](https://code.visualstudio.com/docs/editor/versioncontrol#_merge-conflicts) 
or [GitKraken](https://www.gitkraken.com/blog/merge-conflict-tool) can be used 
to resolve the conflicts for the best possible developer experience.

#### Local Templates

The [existing tools to update templates](#existing-tools-to-update-applied-templates)
that I looked at were only designed to work with templates defined in 
separate Git repositories. This means there was no way to define a template 
locally within the same project, and apply outputs within that project 
and keep them updated.

#### Multiple Template Engines

I also
thought that such a tool could support multiple 
[project generators](#what-is-a-project-or-file-generator), so that everyone
using [project generators](#what-is-a-project-or-file-generator) could take 
advantage of the tool, and even be able to 
[apply it to their existing projects](tutorial/get-started/existing-project.md).
This also improves the whole ecosystem of 
[project generators](#what-is-a-project-or-file-generator), as now you can 
access multiple ecosystems of templates (both Cookiecutter and Copier currently)
and still update everything with [one simple Flexlate command](tutorial/updating.md).

This also has an interesting feature as a side effect: the ability to switch
[project generators](#what-is-a-project-or-file-generator). I actually 
converted my 
[main Python template](https://github.com/nickderobertis/copier-pypi-sphinx-flexlate) 
from a Cookiecutter to a Copier template, and was able to update my projects 
that were previously generated with Cookiecutter without issue. 

#### Files Too

I realized that I could leverage Flexlate not only for generating new projects,
but also for generating files within a project and keeping them up to date.
If you are familiar with the file `generate` part of the 
[Angular CLI](https://angular.io/cli/generate#ng-generate), 
Flexlate acheives a similar interface, 
but with any template that you want. Once you 
[add your template source](tutorial/get-started/add-to-project.md#add-the-template-source), 
you can 
[add as many template outputs anywhere that you want](tutorial/get-started/add-to-project.md#add-template-outputs), 
with just the name of the template. 

#### Solving the Modularity Problem

This ability to generate files instead of entire projects allows building a project up 
with multiple templates.  This is the first part 
of solving the modularity problem. There are planned features to 
use Flexlate projects as templates themselves, and to allow templates to 
coordinate on the behavior of specific files. This will allow for 
arbitrary modularity, allowing to build up projects using standard components
that play well together. Imagine having a JS project and you add a 
the [Jest](https://jestjs.io/) template output and it will create a Jest setup file
as well as adding Jest to your `package.json`. Writing such templates will 
be straightforward once these remaining features are implemented.
