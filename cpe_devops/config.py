from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    base_url: str = 'http://mock-cpe:5000'
    selenium_remote_url: str = 'http://selenium:4444/wd/hub'
    browser: str = 'chrome'
    headless: bool = True
    screenshot_dir: str = 'artifacts/screenshots'


TRUE_VALUES = {'1', 'true', 'yes', 'on'}


def to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


def get_settings() -> Settings:
    return Settings(
        base_url=os.getenv('BASE_URL', Settings.base_url),
        selenium_remote_url=os.getenv('SELENIUM_REMOTE_URL', Settings.selenium_remote_url),
        browser=os.getenv('BROWSER', Settings.browser),
        headless=to_bool(os.getenv('HEADLESS'), default=Settings.headless),
        screenshot_dir=os.getenv('SCREENSHOT_DIR', Settings.screenshot_dir),
    )
