from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    secret_key: str = 'devops-demo-secret'
    admin_username: str = 'admin'
    admin_password: str = 'admin123'
    database_path: str = 'app/data/cpe_gateway.db'
    seed_path: str = 'app/data/state.json'
    api_prefix: str = '/api/v1'
    artifact_dir: str = 'artifacts/firmware'
    device_host: str = '192.168.1.1'
    device_protocol: str = 'mock'
    device_base_url: str = 'http://192.168.1.1'
    device_port: int = 22
    device_username: str = 'admin'
    device_password: str = 'admin'
    device_verify_ssl: bool = False
    serial_port: str = '/dev/ttyUSB0'
    serial_baudrate: int = 115200


def get_settings() -> AppSettings:
    return AppSettings(
        secret_key=os.getenv('APP_SECRET_KEY', AppSettings.secret_key),
        admin_username=os.getenv('ADMIN_USERNAME', AppSettings.admin_username),
        admin_password=os.getenv('ADMIN_PASSWORD', AppSettings.admin_password),
        database_path=os.getenv('DATABASE_PATH', AppSettings.database_path),
        seed_path=os.getenv('SEED_PATH', AppSettings.seed_path),
        api_prefix=os.getenv('API_PREFIX', AppSettings.api_prefix),
        artifact_dir=os.getenv('ARTIFACT_DIR', AppSettings.artifact_dir),
        device_host=os.getenv('DEVICE_HOST', AppSettings.device_host),
        device_protocol=os.getenv('DEVICE_PROTOCOL', AppSettings.device_protocol),
        device_base_url=os.getenv('DEVICE_BASE_URL', AppSettings.device_base_url),
        device_port=int(os.getenv('DEVICE_PORT', str(AppSettings.device_port))),
        device_username=os.getenv('DEVICE_USERNAME', AppSettings.device_username),
        device_password=os.getenv('DEVICE_PASSWORD', AppSettings.device_password),
        device_verify_ssl=os.getenv('DEVICE_VERIFY_SSL', str(AppSettings.device_verify_ssl)).lower() in {'1','true','yes','on'},
        serial_port=os.getenv('SERIAL_PORT', AppSettings.serial_port),
        serial_baudrate=int(os.getenv('SERIAL_BAUDRATE', str(AppSettings.serial_baudrate))),
    )


def resolve_database_path(settings: AppSettings) -> Path:
    return Path(settings.database_path)


def resolve_seed_path(settings: AppSettings) -> Path:
    return Path(settings.seed_path)


def resolve_artifact_dir(settings: AppSettings) -> Path:
    return Path(settings.artifact_dir)
