from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from cpe_devops.config import Settings


SUPPORTED_BROWSERS = {'chrome'}


def create_remote_driver(settings: Settings) -> webdriver.Remote:
    browser = settings.browser.lower()
    if browser not in SUPPORTED_BROWSERS:
        raise ValueError(f'Unsupported browser: {settings.browser}')

    options = Options()
    options.add_argument('--window-size=1440,1080')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    if settings.headless:
        options.add_argument('--headless=new')

    return webdriver.Remote(command_executor=settings.selenium_remote_url, options=options)
