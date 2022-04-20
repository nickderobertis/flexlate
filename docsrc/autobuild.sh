#!/bin/bash
# Note: You likely should be running dev-server.sh directly instead of this
#
# Run this script to auto-build the documentation with changes to source files
# It requires that you have the watchmedo utility installed globally.
# Run `pipx install watchdog[watchmedo]` to install.

WATCH_FILES="source ../flexlate ../README.md"

echo "Starting documentation autoreloader watching $WATCH_FILES"
watchmedo shell-command \
    --patterns="*.py;*.css;*.js;*.md;*.rst" \
    --recursive \
    --command="make github" \
    --drop \
    $WATCH_FILES
