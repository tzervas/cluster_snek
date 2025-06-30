#!/bin/bash
set -e

# Create virtual environment and install dependencies
uv venv .venv
uv pip install --python .venv -e .[dev,test]

# Setup pre-commit hooks
uv pip install pre-commit
pre-commit install

# Configure git commit signing
git config --global user.name "tzervas"
git config --global user.email "tzervas@users.noreply.github.com"
git config --global commit.gpgsign true
echo "$private_gpg" | gpg --import
git config --global user.signingkey "7479B765A6044B0C"

# Activate virtual environment
echo 'source ${workspaceFolder}/.venv/bin/activate' >> ~/.bashrc
