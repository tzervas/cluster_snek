from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
import test_cluster_snek
import test_env_file
import test_generate_project_structure
import test_project_structure
import test_user_settings

import cluster_snek as cs

"""
tests/test_end_to_end.py

End-to-end test for the cluster_snek package.
This test simulates a full workflow from project structure generation to environment variable loading.
"""


if __name__ == "__main__":
    pytest.main([__file__])
    with TemporaryDirectory() as tmpdirname:
        tmp_path = Path(tmpdirname)
        load_env_file(tmp_path)
        test_e2e(tmp_path)

if __name__ == "__main__":
    main()
