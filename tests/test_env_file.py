from pathlib import Path
from tempfile import TemporaryDirectory

from cluster_snek import load_env_file


def test_load_env_file(tmp_path):
    env_content = "FOO=bar\nBAZ=qux\n#COMMENTED=out\n"
    env_path = tmp_path / ".env"
    env_path.write_text(env_content)
    result = load_env_file(env_path)
    assert result == {"FOO": "bar", "BAZ": "qux"}


if __name__ == "__main__":
    with TemporaryDirectory() as tmpdirname:
        tmp_path = Path(tmpdirname)
        test_load_env_file(tmp_path)
