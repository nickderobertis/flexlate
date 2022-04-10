# Making Arbitrary Changes to Flexlate Configuration

Flexlate provides commands that automatically manage configuration such 
as [`fxt add source`](../commands.md#fxt-add-source) or 
[`fxt config target`](../commands.md#fxt-config-target). But not 
every change you might want to make to the config has a command.

## Use `fxt sync` to Bring Arbitrary Changes to Flexlate Branches

Enter [`fxt sync`](../commands.md#fxt-sync) that will take the current 
state of your config and render it to the Flexlate branches before merging
back into your working branch. 

## Possible Uses for `fxt sync`

Why might you want to do this? Let's go through a few examples.

### Moving an Applied Template

For example, say you applied a template but later decide you want 
to move it.

```{run-fxt-terminal}
---
setup: "fxt add source https://github.com/nickderobertis/copier-simple-example"
input: "my answer\n10"
---
fxt add output copier-simple-example some/path
mv some/path other
git add -A
git commit -m 'Move copier-simple-example from some/path to other'
fxt sync
```

### Moving a Template Source

There are several reasons why you might want to move a template source:

- You are using a local template and you want to move it.
- You are using a template from a remote repository and you want to 
  switch it to a fork.
- You are using a template from a remote repository and it was renamed

Just manually update the `flexlate.json` file containing your template 
source, commit the changes, then run 
[`fxt sync`](../commands.md#fxt-sync).

### Updating a Single Applied Template

Flexlate has built-in functionality to update all the applied templates
within a project for a given template source. It does not have a built-in 
command to update a single applied template, but you can do it by manually 
updating the version in the `flexlate.json` file and running 
[`fxt sync`](../commands.md#fxt-sync).

### Migrating Add Modes

Say you have taken the default add mode `local` setting and you are applying
a lot of templates but you don't like having `flexlate.json` files scattered
throughout your project. You want to switch to `project` add mode, but 
Flexlate cannot do this automatically. You can do this manually by 
taking the contents of those `flexlate.json` files and moving them to 
one `flexlate.json` file in your project root. You will need to update the
paths of the applied templates as well as the add mode accordingly. 
Then change the default add mode in `flexlate-project.json` to `project`
so that all new applied templates will use `project` add mode automatically.
Once you have it all done, 
commit your changes and run [`fxt sync`](../commands.md#fxt-sync).