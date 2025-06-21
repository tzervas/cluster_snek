import json

import pytest
import yaml

from cluster_snek import (
    UserSettings, generate_project_structure,
    load_env_file, load_project_structure,
    load_user_settings
)


def test_load_env_file(tmp_path):
    env_content = "FOO=bar\nBAZ=qux\n#COMMENTED=out\n"
    env_path = tmp_path / ".env"
    env_path.write_text(env_content)
    result = load_env_file(env_path)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_load_user_settings_defaults(monkeypatch):
    # Ensure no relevant environment variables are set
    monkeypatch.delenv("PROJECT_NAME", raising=False)
    monkeypatch.delenv("DEPLOYMENT_MODE", raising=False)
    settings = load_user_settings(config_path=None, env_path="nonexistent.env")
    assert isinstance(settings, UserSettings)
    assert settings.project_name == "cluster-snek-homelab"
    assert settings.deployment_mode == settings.settings.DeploymentMode.INTERNET


def test_load_user_settings_from_env(monkeypatch):
    monkeypatch.setenv("PROJECT_NAME", "testproj")
    monkeypatch.setenv("ENABLE_WEBHOOKS", "false")
    monkeypatch.setenv("DEPLOYMENT_MODE", "airgapped-vc")
    settings = load_user_settings(config_path=None, env_path="nonexistent.env")
    assert settings.project_name == "testproj"
    assert settings.enable_webhooks is False
    assert settings.deployment_mode == settings.DeploymentMode.AIRGAPPED_VC


def test_load_user_settings_from_env_file(tmp_path):
    env_content = "project_name=envproj\nenable_webhooks=0\ndeployment_mode=airgapped-local\n"
    env_path = tmp_path / ".env"
    env_path.write_text(env_content)
    settings = load_user_settings(config_path=None, env_path=env_path)
    assert settings.project_name == "envproj"
    assert settings.enable_webhooks is False
    assert settings.deployment_mode == settings.DeploymentMode.AIRGAPPED_LOCAL


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
    assert settings.deployment_mode == settings.DeploymentMode.AIRGAPPED_NETWORK


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
    assert settings.deployment_mode == settings.DeploymentMode.AIRGAPPED_ARCHIVE


def test_load_project_structure_yaml(tmp_path):
    structure = {"foo": {"bar.py": "baz"}}
    yaml_path = tmp_path / "structure.yaml"
    yaml_path.write_text(yaml.dump(structure))
    result = load_project_structure(yaml_path)
    assert result == structure


def test_load_project_structure_json(tmp_path):
    structure = {"foo": {"bar.py": "baz"}}
    json_path = tmp_path / "structure.json"
    json_path.write_text(json.dumps(structure))
    result = load_project_structure(json_path)
    assert result == structure


def test_load_project_structure_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_project_structure(tmp_path / "doesnotexist.yaml")


def test_load_project_structure_unsupported_format(tmp_path):
    bad_path = tmp_path / "structure.txt"
    bad_path.write_text("not a yaml or json")
    with pytest.raises(ValueError):
        load_project_structure(bad_path)


def test_generate_project_structure_creates_files(tmp_path):
    structure = {
        "src": {
            "main.py": "Main entry point",
            "utils.py": "Utility functions"
        },
        "README.md": "# Project Title"
    }
    generate_project_structure(tmp_path, structure)
    assert (tmp_path / "src" / "main.py").exists()
    assert (tmp_path / "src" / "utils.py").exists()
    assert (tmp_path / "README.md").exists()
    # Check Python file content is wrapped in triple quotes
    main_content = (tmp_path / "src" / "main.py").read_text()
    assert main_content.startswith('"""') and main_content.endswith('"""\n')
    # Check non-Python file content
    readme_content = (tmp_path / "README.md").read_text()
    assert readme_content == "# Project Title"


def test_generate_project_structure_skips_unchanged(tmp_path):
    structure = {"foo.py": "abc"}
    generate_project_structure(tmp_path, structure)
    file_path = tmp_path / "foo.py"
    orig_mtime = file_path.stat().st_mtime
    generate_project_structure(tmp_path, structure)
    assert file_path.stat().st_mtime == orig_mtime


def test_generate_project_structure_nested(tmp_path):
    structure = {
        "a": {
            "b": {
                "c.py": "nested"
            }
        }
    }
    generate_project_structure(tmp_path, structure)
    assert (tmp_path / "a" / "b" / "c.py").exists()
    content = (tmp_path / "a" / "b" / "c.py").read_text()
    assert "nested" in content


def main():
    import sys
    from pathlib import Path
    PROJECT_STRUCTURE = load_project_structure()
    target_path = Path(sys.argv[1]) if len(
        sys.argv) > 1 else Path("./cluster-snek-project")
    generate_project_structure(target_path, PROJECT_STRUCTURE)


if __name__ == "__main__":
    main()
