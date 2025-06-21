import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest  # type: ignore
import yaml # type: ignore

from cluster_snek import DeploymentMode, UserSettings, load_user_settings


def test_load_user_settings_defaults(monkeypatch):
    # Ensure no relevant environment variables are set
    monkeypatch.delenv("PROJECT_NAME", raising=False)
    monkeypatch.delenv("DEPLOYMENT_MODE", raising=False)
    settings = load_user_settings(config_path=None, env_path="nonexistent.env")
    assert isinstance(settings, UserSettings)
    assert settings.project_name == "cluster-snek-homelab"
    assert settings.deployment_mode == DeploymentMode.INTERNET


def test_load_user_settings_from_env(monkeypatch):
    monkeypatch.setenv("PROJECT_NAME", "testproj")
    monkeypatch.setenv("ENABLE_WEBHOOKS", "false")
    monkeypatch.setenv("DEPLOYMENT_MODE", "airgapped-vc")
    settings = load_user_settings(config_path=None, env_path="nonexistent.env")
    assert settings.project_name == "testproj"
    assert settings.enable_webhooks is False
    assert settings.deployment_mode == DeploymentMode.AIRGAPPED_VC


def test_load_user_settings_from_env_file(tmp_path):
    env_content = "project_name=envproj\nenable_webhooks=0\ndeployment_mode=airgapped-local\n"
    env_path = tmp_path / ".env"
    env_path.write_text(env_content)
    settings = load_user_settings(config_path=None, env_path=env_path)
    assert settings.project_name == "envproj"
    assert settings.enable_webhooks is False
    assert settings.deployment_mode == DeploymentMode.AIRGAPPED_LOCAL


def test_load_user_settings_from_yaml_config(tmp_path):
    config = {
        "project_name": "yamlproj",
        "enable_webhooks": False,
        "deployment_mode": "airgapped-network"
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.dump(config))
    settings = load_user_settings(
        config_path=config_path, env_path="nonexistent.env")
    assert settings.project_name == "yamlproj"
    assert settings.enable_webhooks is False
    assert settings.deployment_mode == DeploymentMode.AIRGAPPED_NETWORK


def test_load_user_settings_from_json_config(tmp_path):
    config = {
        "project_name": "jsonproj",
        "enable_webhooks": True,
        "deployment_mode": "airgapped-archive"
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    settings = load_user_settings(
        config_path=config_path, env_path="nonexistent.env")
    assert settings.project_name == "jsonproj"
    assert settings.enable_webhooks is True
    assert settings.deployment_mode == DeploymentMode.AIRGAPPED_ARCHIVE

def main():
    with TemporaryDirectory() as tmpdirname:
        tmp_path = Path(tmpdirname)
        test_load_user_settings_defaults(monkeypatch=pytest.MonkeyPatch())
        test_load_user_settings_from_env(monkeypatch=pytest.MonkeyPatch())
        test_load_user_settings_from_env_file(tmp_path)
        test_load_user_settings_from_yaml_config(tmp_path)
        test_load_user_settings_from_json_config(tmp_path)

if __name__ == "__main__":
    main()
