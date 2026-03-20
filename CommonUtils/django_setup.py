from __future__ import annotations

import os
import sys
from pathlib import Path

import django


def _add_sys_path(path: Path) -> None:
    resolved = str(path.resolve())
    if resolved not in sys.path:
        sys.path.insert(0, resolved)


def setup_django(
    project_root: Path, settings_module: str = "django_models.settings", include_database_models: bool = True
) -> None:
    """Initialize Django with project and DatabaseModels paths on sys.path."""
    _add_sys_path(project_root)
    if include_database_models:
        _add_sys_path(project_root / "DatabaseModels")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    django.setup()


def bootstrap_django(
    current_file: str | Path,
    levels_up: int = 2,
    settings_module: str = "django_models.settings",
    include_database_models: bool = True,
) -> None:
    """Derive project root from a file path and initialize Django."""
    project_root = Path(current_file).resolve().parents[levels_up]
    setup_django(
        project_root=project_root,
        settings_module=settings_module,
        include_database_models=include_database_models,
    )
