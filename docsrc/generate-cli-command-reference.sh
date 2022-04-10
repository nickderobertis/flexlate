#!/bin/bash
cd ..
typer flexlate/cli.py utils docs --name fxt --output docsrc/source/commands.md
cd docsrc
