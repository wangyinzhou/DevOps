from __future__ import annotations

from app.config import AppSettings, get_settings, resolve_database_path, resolve_seed_path


def test_get_settings_reads_environment(monkeypatch):
    monkeypatch.setenv('APP_SECRET_KEY', 'secret')
    monkeypatch.setenv('ADMIN_USERNAME', 'ops')
    monkeypatch.setenv('ADMIN_PASSWORD', 'safe-pass')
    monkeypatch.setenv('DATABASE_PATH', 'var/app.db')
    monkeypatch.setenv('SEED_PATH', 'var/state.json')
    monkeypatch.setenv('API_PREFIX', '/api/test')

    settings = get_settings()

    assert settings == AppSettings(
        secret_key='secret',
        admin_username='ops',
        admin_password='safe-pass',
        database_path='var/app.db',
        seed_path='var/state.json',
        api_prefix='/api/test',
    )


def test_resolve_database_and_seed_path_use_settings_values():
    settings = AppSettings(database_path='custom/app.db', seed_path='custom/state.json')

    assert str(resolve_database_path(settings)) == 'custom/app.db'
    assert str(resolve_seed_path(settings)) == 'custom/state.json'
