from __future__ import annotations

from selenium.webdriver.common.by import By

from cpe_devops.pages.base_page import BasePage


class DashboardPage(BasePage):
    def title(self) -> str:
        return self.text_of(By.ID, 'dashboard-title')

    def welcome_text(self) -> str:
        return self.text_of(By.ID, 'welcome-banner')

    def go_to_network(self) -> None:
        self.click(By.ID, 'nav-network')

    def go_to_upgrade(self) -> None:
        self.click(By.ID, 'nav-upgrade')
