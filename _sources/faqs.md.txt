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