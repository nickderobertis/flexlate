# Developing your Own Templates

Flexlate supports both [`cookiecutter`](https://github.com/cookiecutter/cookiecutter) 
and [`copier`](https://github.com/copier-org/copier) templates, so you can 
write your own templates following the guides for those tools.

## Flexlate Development Tools

Flexlate does have a [corresponding development tool](https://nickderobertis.github.io/flexlate-dev/).
Install it and run `dfxt serve` to start a development server in your template 
project, that will render the project with Flexlate in a temporary directory
and auto-update it as you make changes in the template.

It also has a `dfxt publish` command that will render your template and 
create a new project with it. This is useful along with a 
CI pipeline to automatically create and sync example repositories with 
output from your template.
