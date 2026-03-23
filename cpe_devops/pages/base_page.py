from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver: WebDriver, base_url: str, timeout: int = 10) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip('/')
        self.wait = WebDriverWait(driver, timeout)

    def open(self, path: str) -> None:
        self.driver.get(f'{self.base_url}{path}')

    def click(self, by: str, value: str) -> None:
        self.wait.until(EC.element_to_be_clickable((by, value))).click()

    def fill(self, by: str, value: str, text: str) -> None:
        element = self.wait.until(EC.visibility_of_element_located((by, value)))
        element.clear()
        element.send_keys(text)

    def text_of(self, by: str, value: str) -> str:
        return self.wait.until(EC.visibility_of_element_located((by, value))).text

    def current_url(self) -> str:
        return self.driver.current_url

    @staticmethod
    def by_id(element_id: str) -> tuple[str, str]:
        return By.ID, element_id
