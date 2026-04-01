from __future__ import annotations

from selenium.webdriver.common.by import By

from cpe_devops.pages.base_page import BasePage


class UpgradePage(BasePage):
    def upload_filename(self, filename: str) -> None:
        self.fill(By.ID, 'firmware-file', filename)
        self.click(By.ID, 'upload-btn')

    def message(self) -> str:
        return self.text_of(By.ID, 'upgrade-message')

    def status(self) -> str:
        return self.text_of(By.ID, 'upgrade-status')
