from pathlib import Path
from tempfile import TemporaryDirectory

from cluster_snek import generate_project_structure, load_env_file


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


if __name__ == "__main__":
    with TemporaryDirectory() as tmpdirname:
        tmp_path = Path(tmpdirname)
        load_env_file(tmp_path)
        test_generate_project_structure_creates_files(tmp_path)
        test_generate_project_structure_skips_unchanged(tmp_path)
        test_generate_project_structure_nested(tmp_path)
