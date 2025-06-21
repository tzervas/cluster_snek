import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest # type: ignore
import yaml # type: ignore

from cluster_snek import load_env_file, load_project_structure


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


if __name__ == "__main__":
    pytest.main([__file__])
    with TemporaryDirectory() as tmpdirname:
        tmp_path = Path(tmpdirname)
        load_env_file(tmp_path)
    test_load_project_structure_yaml(tmp_path)
    test_load_project_structure_json(tmp_path)
    test_load_project_structure_file_not_found(tmp_path)
    test_load_project_structure_unsupported_format(tmp_path)
