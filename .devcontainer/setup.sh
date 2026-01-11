#!/bin/bash
set -e

# Ensure WORKSPACE_FOLDER is set
: "${WORKSPACE_FOLDER:=/workspace}"
if [ -z "$WORKSPACE_FOLDER" ]; then
  echo "Error: WORKSPACE_FOLDER is not set or empty." >&2
  exit 1
fi

# Load environment variables
if [ ! -d "$WORKSPACE_FOLDER" ]; then
  echo "Creating workspace directory: $WORKSPACE_FOLDER"
  mkdir -p "$WORKSPACE_FOLDER"
fi

if [ -f "${WORKSPACE_FOLDER}/.env" ]; then
    source "${WORKSPACE_FOLDER}/.env"
else
    echo "Warning: .env file not found. Using default values."
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a Python package is installed
python_package_installed() {
    python3 -c "import $1" >/dev/null 2>&1
}

# Create virtual environment if it doesn't exist
if [ ! -d "$WORKSPACE_FOLDER" ]; then
  echo "Creating workspace directory: $WORKSPACE_FOLDER"
  mkdir -p "$WORKSPACE_FOLDER"
fi

if [ ! -d "${WORKSPACE_FOLDER}/.venv" ]; then
    echo "Creating virtual environment..."
    uv venv "${WORKSPACE_FOLDER}/.venv"
fi

# Install project dependencies
echo "Installing project dependencies..."
uv pip install --python "${WORKSPACE_FOLDER}/.venv" -e .[dev,test]

# Setup pre-commit hooks if enabled
if [ "${ENABLE_PRECOMMIT:-true}" = "true" ]; then
    PRECOMMIT_BIN="${WORKSPACE_FOLDER}/.venv/bin/pre-commit"
    if [ ! -x "$PRECOMMIT_BIN" ]; then
        echo "Installing pre-commit..."
        uv pip install pre-commit
    fi
    # Install pre-commit hooks using the venv's pre-commit binary
    "${WORKSPACE_FOLDER}/.venv/bin/pre-commit" install
fi

# Configure git if not already configured
if ! git config --global --get user.email >/dev/null 2>&1; then
    echo "Configuring Git..."
    git config --global user.name "${GITHUB_USERNAME:-tzervas}"
    git config --global user.email "${GITHUB_EMAIL:-tzervas@users.noreply.github.com}"
    git config --global commit.gpgsign true
fi

# Configure GPG if not already configured
GPG_KEY_ID="${GPG_KEY_ID:-7479B765A6044B0C}"
if ! gpg --list-keys "${GPG_KEY_ID}" >/dev/null 2>&1; then
    echo "Configuring GPG..."
    if [ -n "${private_gpg}" ]; then
        echo "${private_gpg}" | gpg --import
        git config --global user.signingkey "${GPG_KEY_ID}"
    fi
fi

# Add virtual environment activation to bashrc if not already present
ACTIVATE_CMD="source ${WORKSPACE_FOLDER}/.venv/bin/activate"
if ! grep -q "${ACTIVATE_CMD}" ~/.bashrc; then
    echo "Adding virtual environment activation to .bashrc"
    echo "${ACTIVATE_CMD}" >> ~/.bashrc
fi

# Create necessary directories
if [ ! -d "$WORKSPACE_FOLDER" ]; then
  echo "Creating workspace directory: $WORKSPACE_FOLDER"
  mkdir -p "$WORKSPACE_FOLDER"
fi

mkdir -p "${WORKSPACE_FOLDER}/logs"
mkdir -p "${WORKSPACE_FOLDER}/data"

echo "Development environment setup complete!"
