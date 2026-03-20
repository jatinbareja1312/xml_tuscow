from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    current_dir = Path(__file__).resolve().parent
    tests_path = current_dir / "bootstrap_upsert_graph" / "tests" / "test_upsert_graph.py"
    subprocess.check_call([sys.executable, "-m", "pytest", str(tests_path), "-q"])


if __name__ == "__main__":
    main()
