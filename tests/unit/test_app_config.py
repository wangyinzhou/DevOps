from __future__ import annotations

from app.config import AppSettings, get_settings, resolve_state_path


def test_get_settings_reads_environment(monkeypatch):
    monkeypatch.setenv('APP_SECRET_KEY', 'secret')
    monkeypatch.setenv('ADMIN_USERNAME', 'ops')
    monkeypatch.setenv('ADMIN_PASSWORD', 'safe-pass')
    monkeypatch.setenv('STATE_PATH', 'var/state.json')
    monkeypatch.setenv('API_PREFIX', '/api/test')

    settings = get_settings()

    assert settings == AppSettings(
        secret_key='secret',
        admin_username='ops',
        admin_password='safe-pass',
        state_path='var/state.json',
        api_prefix='/api/test',
    )


def test_resolve_state_path_uses_settings_value():
    settings = AppSettings(state_path='custom/state.json')

    assert str(resolve_state_path(settings)) == 'custom/state.json'
