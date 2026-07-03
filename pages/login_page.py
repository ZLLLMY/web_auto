from selenium.webdriver.common.by import By


class LoginPage:

    def __init__(self, driver):
        self.driver = driver
        self._name_field = (By.CSS_SELECTOR, 'input[name="name"]:nth-child(2)')
        self._email_field = (By.ID, 'exampleInputPassword1')
        self._password_field = (By.CSS_SELECTOR, 'input[name="email"]')


    def login(self, name, email, password):
        self.driver.find_element(*self._name_field).send_keys(name)
        self.driver.find_element(*self._email_field).send_keys(email)
        self.driver.find_element(*self._password_field).send_keys(password)
