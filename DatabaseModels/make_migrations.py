from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import django
from django.core.management import call_command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Django migrations")
    parser.add_argument(
        "--skip-makemigrations",
        action="store_true",
        help="Skip makemigrations and only run migrate",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(current_dir))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_models.settings")

    django.setup()

    if not args.skip_makemigrations:
        call_command("makemigrations", "django_models")

    call_command("migrate", fake_initial=True)


if __name__ == "__main__":
    main()
