#!/bin/bash
# Run this script to auto-reload the documentation with changes to source files
# Requirements:
# The watchmedo utility must installed globally:
# Run `pipx install watchdog[watchmedo]` to install.
# The live-server utility must also be installed globally:
# Run `npm install -g live-server` to install.


# Ensure that the auto-build exits when the script exits
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

echo "Starting dev server"

# Watches package, docsrc, and README.md to build docs with Sphinx into a static HTML site
./autobuild.sh &

# Watches static site output and live reloads browser in response to it
live-server ../docs
