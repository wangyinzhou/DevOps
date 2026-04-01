from __future__ import annotations

import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from _pytest.runner import CallInfo

from cpe_devops.config import get_settings
from cpe_devops.utils.artifacts import screenshot_path

try:
    import allure
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal environments
    class _AttachmentType:
        PNG = 'image/png'

    class _AllureFallback:
        attachment_type = _AttachmentType()

        class attach:
            @staticmethod
            def file(*args, **kwargs):
                return None

    allure = _AllureFallback()


@pytest.fixture(scope='session')
def settings():
    return get_settings()


@pytest.fixture(scope='session')
def base_url(settings):
    return settings.base_url


@pytest.fixture()
def driver(settings):
    from cpe_devops.utils.driver_factory import create_remote_driver

    driver = create_remote_driver(settings)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call: CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f'rep_{report.when}', report)


@pytest.fixture(autouse=True)
def attach_failure_artifacts(request, settings):
    yield
    report = getattr(request.node, 'rep_call', None)
    driver = request.node.funcargs.get('driver') if hasattr(request.node, 'funcargs') else None
    if report and report.failed and driver:
        file_path = screenshot_path(settings.screenshot_dir, request.node.nodeid)
        driver.save_screenshot(str(file_path))
        allure.attach.file(str(file_path), name=f'screenshot-{int(time.time())}', attachment_type=allure.attachment_type.PNG)
