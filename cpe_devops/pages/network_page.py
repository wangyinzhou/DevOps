from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from cpe_devops.pages.base_page import BasePage


class NetworkPage(BasePage):
    def save_network(self, ssid: str, password: str, mode: str) -> None:
        self.fill(By.ID, 'ssid', ssid)
        self.fill(By.ID, 'wifi-password', password)
        Select(self.driver.find_element(By.ID, 'mode')).select_by_value(mode)
        self.click(By.ID, 'save-network')

    def message(self) -> str:
        return self.text_of(By.ID, 'network-message')
