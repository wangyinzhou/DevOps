from __future__ import annotations

import pytest

from cpe_devops.pages.dashboard_page import DashboardPage
from cpe_devops.pages.login_page import LoginPage
from cpe_devops.pages.network_page import NetworkPage
from cpe_devops.pages.upgrade_page import UpgradePage


@pytest.mark.ui
@pytest.mark.smoke
def test_admin_can_login(driver, base_url):
    login_page = LoginPage(driver, base_url)
    dashboard_page = DashboardPage(driver, base_url)

    login_page.load()
    login_page.login('admin', 'admin123')

    assert '控制台' in dashboard_page.title()
    assert 'admin' in dashboard_page.welcome_text()


@pytest.mark.ui
def test_network_settings_can_be_saved(driver, base_url):
    login_page = LoginPage(driver, base_url)
    dashboard_page = DashboardPage(driver, base_url)
    network_page = NetworkPage(driver, base_url)

    login_page.load()
    login_page.login('admin', 'admin123')
    dashboard_page.go_to_network()
    network_page.save_network('Lab-CPE', 'N3tworkPass!', 'pppoe')

    assert '已保存' in network_page.message()


@pytest.mark.ui
def test_invalid_firmware_file_is_rejected(driver, base_url):
    login_page = LoginPage(driver, base_url)
    dashboard_page = DashboardPage(driver, base_url)
    upgrade_page = UpgradePage(driver, base_url)

    login_page.load()
    login_page.login('admin', 'admin123')
    dashboard_page.go_to_upgrade()
    upgrade_page.upload_filename('firmware.txt')

    assert '.bin' in upgrade_page.message()
    assert 'rejected' in upgrade_page.status()
