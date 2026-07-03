import inspect
import logging
import os
from datetime import datetime, timedelta
import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


@pytest.mark.usefixtures("invokeBrowser")
class BaseClass:
    driver: WebDriver   # ✅ Type hint for IntelliSense

    # def getLogger(self):
    #     testCaseName = inspect.stack()[1][3]
    #     logger = logging.getLogger(testCaseName)
    #     os.makedirs("logs", exist_ok=True)
    #     log_file_name = f"logs/log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    #     logger.log_path = f"logs/{log_file_name}"
    #     fileHandler = logging.FileHandler(log_file_name)
    #     formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
    #     fileHandler.setFormatter(formatter)
    #     logger.addHandler(fileHandler)
    #     logger.setLevel(logging.DEBUG)
    #     return logger

    def selectByVisibleText(self, locator, text):
        select = Select(locator)
        select.select_by_visible_text(text)
        print(text+" has been selected in dropdown")

    def selectByValue(self, locator, value):
        select = Select(locator)
        select.select_by_value(value)
        print(value+" has been selected in dropdown")

    def selectByIndex(self, locator, index):
        select = Select(locator)
        select.select_by_index(index)
        print(index+" has been selected in dropdown")

    def elementShouldBeVisible(self, locator):
        assert locator.is_displayed(), f"Element {locator} is not visible on the screen."
        print(f"Element {locator} is visible.")

    def elementShouldNotBeVisible(self, locator):
        assert not locator.is_displayed(), (f"Element {locator} is visible.")
        print(f"Element {locator} is not visible.")

    def scroll_element_into_view(self, locator):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", locator)

    def get_todays_date(self, format):
        return datetime.today().strftime(format)

    def getFutureDate(self, days_ahead, format):
        futureDate = datetime.today() + timedelta(days=days_ahead)
        return futureDate.strftime(format)

    def elementShouldBePresent(self, locatorVariable):
        try:
            WebDriverWait(self.driver, 5).until(expected_conditions.visibility_of_element_located(locatorVariable))
            return True
        except:
            return False

    def elementShouldNotBePresent(self, locatorVariable):
        try:
            WebDriverWait(self.driver, 5).until(expected_conditions.invisibility_of_element_located(locatorVariable))
            return True
        except:
            return False
