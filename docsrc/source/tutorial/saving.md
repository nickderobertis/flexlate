# Save your Flexlate Updates

Flexlate [saves the history of your merge conflict resolutions](../core-concepts.md#branches-for-flexlate-operations) 
so that you don't need to resolve them multiple times. Flexlate mostly manages 
this history for you, but you do get to choose when you want to 
"save" the history by merging the [Flexlate feature branches](../core-concepts.md#flexlate-feature-branches) 
into the 
[Flexlate main branches](../core-concepts.md#flexlate-main-branches). 

After doing a Flexlate operation such as
[`fxt update`](../commands.md#fxt-update), 
[`fxt add output`](../commands.md#fxt-add-output), or
[`fxt sync`](../commands.md#fxt-sync) Flexlate will create feature branches 
to correspond to your currently checked out branch. In order to save the
Flexlate history, you need to merge these Flexlate feature branches into 
the Flexlate main branches.

## Local Workflows

If directly commit to the main branch or locally merge branches into 
your main branch, you will want to use the 
[`fxt merge`](../commands.md#fxt-merge) command locally to save your history.
You can then push the changes to remote with 
[`fxt push main`](../commands.md#fxt-push-main)

### Committing on the Main Branch

If you commit on the main branch, let's call it `main`, you will have 
Flexlate feature branches created corresponding to your main branch. 
Simply call `fxt merge` whenever you finish a Flexlate operation 
and are satisfied with the result.

```{run-fxt-terminal}
---
setup: "fxt add source https://github.com/nickderobertis/copier-simple-example"
input: "my answer\n10"
---
fxt add output copier-simple-example some/path
fxt merge
```

### Locally Merging Branches

After you've done a template update on a feature branch and you're ready
to merge the changes into main, first run `fxt merge` before doing so.

```{run-fxt-terminal}
---
setup: "fxt add source https://github.com/nickderobertis/copier-simple-example"
input: "[None, 'my answer\\n10']"
---
git checkout -b feature-branch
fxt add output copier-simple-example some/path
fxt merge
git checkout master
git merge feature-branch
```

### Push your Flexlate Main Branch Changes

After you've merged the Flexlate feature branches into the Flexlate main 
branches, you'll want to push your changes to the remote (if you are using
a remote) via [`fxt push main`](../commands.md#fxt-push-main). 

```{run-fxt-terminal}
---
setup: "fxt add source https://github.com/nickderobertis/copier-simple-example && rm -rf ../remote && mkdir ../remote && git init ../remote && git remote add origin ../remote"
input: "my answer\n10"
---
fxt add output copier-simple-example some/path
fxt merge
fxt push main
```

## PR Workflows

If you use pull requests in your project to merge changes into the main branch, 
then instead of merging locally, you will want to push the Flexlate 
feature branches with [`fxt push feature`](../commands.md#fxt-push-feature)
so that they can be merged in on the remote.

### Push your Flexlate Feature Branch Changes

Use the [`fxt push feature`](../commands.md#fxt-push-feature) command to push
the Flexlate feature branches after you've finished work on your feature branch.
You would want to run this whenever you are pushing up the feature branch itself.

```{run-fxt-terminal}
---
setup: "fxt add source https://github.com/nickderobertis/copier-simple-example && rm -rf ../remote && mkdir ../remote && git init ../remote && git remote add origin ../remote"
input: "[None, 'my answer\\n10']"
---
git checkout -b feature-branch
fxt add output copier-simple-example some/path
git push origin feature-branch
fxt push feature
```

### Merge Flexlate Branches Automatically with Github Actions

Flexlate has 
[official companion Github Actions](../core-concepts.md#ci-workflows)
that can automate using Flexlate. The 
[Flexlate Merge Action](https://github.com/nickderobertis/flexlate-merge-action) 
can be used to automate merging the Flexlate feature branches into the 
Flexlate main branches.

Follow the [user guide on CI automation](ci-automation.md) 
to hook up this workflow and 
other supporting workflows.