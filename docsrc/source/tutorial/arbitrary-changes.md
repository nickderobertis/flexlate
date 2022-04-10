# Making Arbitrary Changes to Flexlate Configuration

Flexlate provides commands that automatically manage configuration such 
as [`fxt add source`](../commands.md#fxt-add-source) or 
[`fxt config target`](../commands.md#fxt-config-target). But not 
every change you might want to make to the config has a command.

## Use `fxt sync` to Bring Arbitrary Changes to Flexlate Branches

Enter [`fxt sync`](../commands.md#fxt-sync) that will take the current 
state of your config and render it to the Flexlate branches before merging
back into your working branch. 

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