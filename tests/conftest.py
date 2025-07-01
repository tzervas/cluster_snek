"""Test configuration and fixtures for Cluster Snek."""

import os
import pytest
from pathlib import Path
from typing import Generator

from cluster_snek.core.config import Config
from cluster_snek.core.context import Context, set_context

@pytest.fixture
def temp_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)

@pytest.fixture
def test_config() -> Config:
    """Create a test configuration."""
    return Config(
        project_name="test-project",
        environment="test",
        deployment_mode="internet",
        clusters=[],
    )

@pytest.fixture
def test_context(temp_dir: Path) -> Context:
    """Create a test context."""
    ctx = Context(
        config_path=temp_dir / "config.yaml",
        work_dir=temp_dir,
        debug=True,
        env={
            "GITHUB_TOKEN": "test-token",
            "GITHUB_USERNAME": "test-user",
            "GITHUB_EMAIL": "test@example.com",
            "GPG_KEY_ID": "test-key",
            "GPG_KEY_EMAIL": "test@example.com",
        },
    )
    set_context(ctx)
    return ctx
