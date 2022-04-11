# Undo Flexlate Operations

Flexlate commits to branches as it makes changes, so reversing changes 
is not as simple as resetting the working directory.

There are two ways to undo a Flexlate operation: via 
[`fxt undo`](../commands.md#fxt-undo) or by deleting the Flexlate 
feature branches.

## Undo Operations with `fxt undo`

Think of `fxt undo` as `CTRL/CMD + Z` for Flexlate. It reverses the Git 
history to undo the last transaction. Flexlate puts transaction markers in 
all its commit messages, and it will only undo commits with a marker 
or merging a commit with a marker.

```{warning}
Flexlate has multiple protections in place to avoid deleting your 
changes, but it still **deletes Git history**. It is recommended to 
only use this command if you are following a feature branch workflow.
```

```{run-fxt-terminal}
---
setup: "fxt add source https://github.com/nickderobertis/copier-simple-example"
input: "my answer\n10"
---
fxt add output copier-simple-example
ls
fxt undo
ls
```

## Undo Operations by Deleting Feature Branches

Flexlate saves the history of your operations on the 
[Flexlate feature branches](../core-concepts.md#flexlate-feature-branches)  
that need to be [merged into the main branches to permanently save](saving.md).
If you have not yet merged the feature branches into the main branches, and you
want to reverse all operations you've made on this feature branch, you can
simply delete the Flexlate feature branches.

```{run-fxt-terminal}
---
setup: "fxt add source https://github.com/nickderobertis/copier-simple-example && fxt merge"
input: "[None, 'my answer\\n10']"
---
git checkout -b my-feature
fxt add output copier-simple-example
ls
git checkout master
git branch -D my-feature
git branch -D flexlate-templates-my-feature
git branch -D flexlate-output-my-feature
ls
```