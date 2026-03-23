from __future__ import annotations

from cpe_devops.config import Settings, get_settings, to_bool


def test_to_bool_handles_truthy_and_default(monkeypatch):
    assert to_bool('true') is True
    assert to_bool('YES') is True
    assert to_bool(None, default=True) is True
    assert to_bool('false') is False


def test_get_settings_reads_environment(monkeypatch):
    monkeypatch.setenv('BASE_URL', 'http://127.0.0.1:5000')
    monkeypatch.setenv('SELENIUM_REMOTE_URL', 'http://127.0.0.1:4444/wd/hub')
    monkeypatch.setenv('BROWSER', 'chrome')
    monkeypatch.setenv('HEADLESS', 'false')
    monkeypatch.setenv('SCREENSHOT_DIR', 'tmp/screens')

    settings = get_settings()

    assert settings == Settings(
        base_url='http://127.0.0.1:5000',
        selenium_remote_url='http://127.0.0.1:4444/wd/hub',
        browser='chrome',
        headless=False,
        screenshot_dir='tmp/screens',
    )
