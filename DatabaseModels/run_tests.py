from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent

    env = os.environ.copy()
    env.setdefault("SQLITE_PATH", "/tmp/xml_tuscow.sqlite3")

    subprocess.check_call([sys.executable, str(current_dir / "manage.py"), "check"], env=env)
    subprocess.check_call(
        [sys.executable, "-m", "pytest", str(project_root / "Jobs/bootstrap_upsert_graph/tests/test_upsert_graph.py"), "-q"],
        env=env,
    )


if __name__ == "__main__":
    main()
