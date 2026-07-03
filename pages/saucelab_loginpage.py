from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


class SauselabLoginPage:
    driver: WebDriver

    def __init__(self, driver):
        self.driver = driver

    _USERNAME_FIELD = (By.CSS_SELECTOR, '[id="user-name"]')
    _PASSWORD_FIELD = (By.CSS_SELECTOR, '[id="password"]')
    _LOGIN_BUTTON = (By.CSS_SELECTOR, '[id="login-button"]')

    def get_username_field(self):
        return self.driver.find_element(*SauselabLoginPage._USERNAME_FIELD)

    def get_password_field(self):
        return self.driver.find_element(*SauselabLoginPage._PASSWORD_FIELD)

    def get_login_button(self):
        return self.driver.find_element(*SauselabLoginPage._LOGIN_BUTTON)