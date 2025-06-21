#!/bin/bash
set -e
uv venv .venv
uv pip install --python .venv -e .[test]
echo 'source ${workspaceFolder}/.venv/bin/activate' >> ~/.bashrc
