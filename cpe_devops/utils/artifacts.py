from __future__ import annotations

from pathlib import Path


def ensure_directory(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def screenshot_path(directory: str, test_name: str) -> Path:
    safe_name = test_name.replace('/', '_').replace(' ', '_')
    return ensure_directory(directory) / f'{safe_name}.png'
