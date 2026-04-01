from __future__ import annotations

from pathlib import Path

from app.config import AppSettings, get_settings, resolve_database_path, resolve_seed_path


def test_get_settings_reads_environment(monkeypatch):
    monkeypatch.setenv('APP_SECRET_KEY', 'secret')
    monkeypatch.setenv('ADMIN_USERNAME', 'ops')
    monkeypatch.setenv('ADMIN_PASSWORD', 'safe-pass')
    monkeypatch.setenv('DATABASE_PATH', 'var/app.db')
    monkeypatch.setenv('SEED_PATH', 'var/state.json')
    monkeypatch.setenv('API_PREFIX', '/api/test')
    monkeypatch.setenv('DEVICE_PROTOCOL', 'http')
    monkeypatch.setenv('DEVICE_BASE_URL', 'https://192.168.1.1')
    monkeypatch.setenv('DEVICE_PORT', '2222')
    monkeypatch.setenv('DEVICE_USERNAME', 'root')
    monkeypatch.setenv('DEVICE_PASSWORD', 'pass')
    monkeypatch.setenv('DEVICE_VERIFY_SSL', 'true')
    monkeypatch.setenv('SERIAL_PORT', '/dev/ttyS1')
    monkeypatch.setenv('SERIAL_BAUDRATE', '57600')

    settings = get_settings()

    assert settings == AppSettings(
        secret_key='secret',
        admin_username='ops',
        admin_password='safe-pass',
        database_path='var/app.db',
        seed_path='var/state.json',
        api_prefix='/api/test',
        device_protocol='http',
        device_base_url='https://192.168.1.1',
        device_port=2222,
        device_username='root',
        device_password='pass',
        device_verify_ssl=True,
        serial_port='/dev/ttyS1',
        serial_baudrate=57600,
    )


def test_resolve_database_and_seed_path_use_settings_values():
    settings = AppSettings(database_path='custom/app.db', seed_path='custom/state.json')

    assert resolve_database_path(settings) == Path('custom/app.db')
    assert resolve_seed_path(settings) == Path('custom/state.json')
