# Update Templates

One of the big advantages of Flexlate is the ease of bringing updates 
to the template back to your project. Flexlate creates [real Git merge 
conflicts](../core-concepts.md#real-merge-conflicts), so you can use your preferred merge tool to resolve them.
Flexlate [saves the resolved conflicts in Git branches](../core-concepts.md#git-native), so you won't 
have to resolve the same conflicts again on the next update.

## Updating Templates

The [`fxt update`](../commands.md#fxt-update) command updates the template(s)
to the latest version allowed. It can also be used to update the data 
with or without updating the version.

```{run-fxt-terminal}
---
setup: "fxt init-from https://github.com/nickderobertis/copier-simple-example --no-input --version c7e1ba1bfb141e9c577e7c21ee4a5d3ae5dde04d --folder-name my-project && cd my-project && fxt config target copier-simple-example"
input: "[None, '\\n50']"
---
cat answer1.txt
fxt update
cat answer1.txt
```

By default, it will prompt for all the questions, using the saved answers
as defaults. You can change any data that you want during the update process.

### Updating without Prompts

If you want to use the existing data and skip all prompts, you can 
pass the `--no-input` flag or `-n` for short:

```shell
fxt update -n
```

### Updating specific Templates


You can update specific templates by passing the names of the template
sources you want to update, for example:

```shell
fxt update copier-simple-example
```

### Checking for Updates

The [`fxt check`](../commands.md#fxt-check) command 
checks for updates to the template(s). It displays 
them in a tabular format if there are updates available.

```{run-fxt-terminal}
---
setup: "fxt init-from https://github.com/nickderobertis/copier-simple-example --no-input --version c7e1ba1bfb141e9c577e7c21ee4a5d3ae5dde04d --folder-name my-project && cd my-project"
allow-exceptions: True
---
fxt check
fxt config target copier-simple-example
fxt check
```

For scripting purposes, it returns code `0` if there are no updates available,
and `1` if there are:

```shell
if ! fxt check; then
  echo "Need to update template";
else
  echo "No updates to template needed";
fi;
```

###  Change Target Version

Normally, the target version in a template source will be set to `null`, 
meaning `fxt update` will always update to the newest version. If a template 
source was added with the `--version` flag, then it will have that version
set as the target version. When the target version is specified for a template
source, `fxt update` will not update beyond that version.

To remove the target version, use the 
[`fxt config target`](../commands.md#fxt-config-target) command to remove 
the target version. 

```{run-fxt-terminal}
---
input: "my answer\n10\n"
---
fxt init-from https://github.com/nickderobertis/copier-simple-example --version c7e1ba1bfb141e9c577e7c21ee4a5d3ae5dde04d
cd project
cat flexlate.json | grep target
fxt config target copier-simple-example
cat flexlate.json | grep target
cat 'my answer.txt'
fxt update --no-input
cat 'my answer.txt'
```

## Get Automated PRs with Template Updates

Flexlate has 
[official companion Github Actions](../core-concepts.md#ci-workflows)
that can automate using Flexlate. The 
[Flexlate Update Action](https://github.com/nickderobertis/flexlate-update-action) 
can be used to help automatically get PRs for template updates. 

If there is a merge conflict in the changes, it will open a separate 
PR to resolve the conflicts, allowing you to resolve them in Github's
web editor.

Follow the [user guide on CI automation](ci-automation.md) 
to hook up this workflow and 
other supporting workflows.

## Next Steps

In order to keep updating and not have to resolve the same merge conflicts 
repeatedly, we need to [save the Flexlate history](saving.md). 