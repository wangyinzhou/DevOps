from __future__ import annotations

from cpe_devops.utils.artifacts import ensure_directory, screenshot_path


def test_ensure_directory_creates_path(tmp_path):
    target = tmp_path / 'reports' / 'screenshots'

    created = ensure_directory(str(target))

    assert created.exists()
    assert created.is_dir()


def test_screenshot_path_sanitizes_test_name(tmp_path):
    path = screenshot_path(str(tmp_path), 'tests/ui/test_demo.py::test login')

    assert path.parent == tmp_path
    assert path.name == 'tests_ui_test_demo.py::test_login.png'
