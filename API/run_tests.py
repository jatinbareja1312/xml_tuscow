from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    db_manage = project_root / "DatabaseModels" / "manage.py"

    env = os.environ.copy()
    env.setdefault("SQLITE_PATH", "/tmp/xml_tuscow.sqlite3")

    subprocess.check_call([sys.executable, str(db_manage), "test", "API.tests", "-v", "2"], env=env)


if __name__ == "__main__":
    main()
