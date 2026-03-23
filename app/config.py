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
    )


def resolve_database_path(settings: AppSettings) -> Path:
    return Path(settings.database_path)


def resolve_seed_path(settings: AppSettings) -> Path:
    return Path(settings.seed_path)


def resolve_artifact_dir(settings: AppSettings) -> Path:
    return Path(settings.artifact_dir)
