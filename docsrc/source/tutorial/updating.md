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
If you want to use the existing data and skip all prompts, you can 
pass the `--no-input` flag or `-n` for short:

```shell
fxt update -n
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
can be used to help automatically get PRs for template updates. Here's an 
example Github Actions workflow that uses the Flexlate Update Action to 
check once a day for updates to the templates and create a PR for them:

```yaml
name: Update Template using Flexlate

on:
  schedule:
    - cron: "0 3 * * *" # every day at 3:00 AM
  workflow_dispatch:

jobs:
  templateUpdate:
    runs-on: ubuntu-latest
    strategy:
      max-parallel: 1
      matrix:
        python-version: [3.8]

    steps:
      - uses: actions/checkout@v3
        with:
          ref: ${{ github.ref_name }}
          fetch-depth: 0
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v1
        with:
          python-version: ${{ matrix.python-version }}
      - uses: nickderobertis/flexlate-update-action@main
        with:
          gh_token: ${{ secrets.gh_token }}

```

Both `actions/checkout` and `actions/setup-python` must be run
before the Flexlate Update Action. `actions/checkout` must be 
run with `fetches-depth: 0` so that all branches and history 
are fetched.

## Next Steps

In order to keep updating and not have to resolve the same merge conflicts 
repeatedly, we need to [save the Flexlate history](saving.md). 