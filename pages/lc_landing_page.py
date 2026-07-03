from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


class LC_Landing_Page:
    driver: WebDriver

    def __init__(self, driver):
        self.driver = driver

    _WORKSPACE_TAB = (By.CSS_SELECTOR, '[href="/test"]:nth-child(1)')

    def get_workspace_tab(self):
        return self.driver.find_element(*LC_Landing_Page._WORKSPACE_TAB)

