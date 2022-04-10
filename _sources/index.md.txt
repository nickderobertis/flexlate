% flexlate documentation master file, created by
%   copier-pypi-sphinx-flexlate.
%   You can adapt this file completely to your liking, but it should at least
%   contain the root `toctree` directive.

# Welcome to Flexlate documentation!

```{include} ../../README.md
```

For more information on getting started, take a look at the tutorial and examples.

## Tutorial and Examples

```{toctree}
---
maxdepth: 2
---

core-concepts
tutorial/index
CLI Reference <commands>
```

## API Documentation

```{eval-rst}
.. toctree:: Python API Reference <api/modules>
   :maxdepth: 1
```

## Indices

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
