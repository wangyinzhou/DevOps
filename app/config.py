from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    secret_key: str = 'devops-demo-secret'
    admin_username: str = 'admin'
    admin_password: str = 'admin123'
    state_path: str = 'app/data/state.json'
    api_prefix: str = '/api/v1'


def get_settings() -> AppSettings:
    return AppSettings(
        secret_key=os.getenv('APP_SECRET_KEY', AppSettings.secret_key),
        admin_username=os.getenv('ADMIN_USERNAME', AppSettings.admin_username),
        admin_password=os.getenv('ADMIN_PASSWORD', AppSettings.admin_password),
        state_path=os.getenv('STATE_PATH', AppSettings.state_path),
        api_prefix=os.getenv('API_PREFIX', AppSettings.api_prefix),
    )


def resolve_state_path(settings: AppSettings) -> Path:
    return Path(settings.state_path)
