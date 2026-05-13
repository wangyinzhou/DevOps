from __future__ import annotations

from selenium.webdriver.common.by import By

from cpe_devops.pages.base_page import BasePage


class LoginPage(BasePage):
    path = '/login'

    def load(self) -> None:
        self.open(self.path)

    def login(self, username: str, password: str) -> None:
        self.fill(By.ID, 'username', username)
        self.fill(By.ID, 'password', password)
        self.click(By.ID, 'login-btn')

    def error_message(self) -> str:
        return self.text_of(By.ID, 'error-message')
