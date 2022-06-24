#!/bin/bash
# A script for running pip-compile passing multiple files through lint-staged

echo "$@" | xargs -n1 pip-compile --upgrade --generate-hashes