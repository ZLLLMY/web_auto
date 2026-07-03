import time

from selenium import webdriver

from base.base_class import BaseClass
from conftest import capture_screenshot
from pages.lc_landing_page import LC_Landing_Page


class Test_Input_Field_Fn(BaseClass):

    def test_inputfield_validations(self, request, load_config, logger):
        logger.info("Launching the Browser and Navigating into LetCode.in website")
        self.driver.get(load_config['letcode_url'])
        logger.info("Maximize the browser window")
        self.driver.maximize_window()
        time.sleep(2)
        logger.info("Click on the Tab")
        lc_land_page = LC_Landing_Page(self.driver)
        lc_land_page.get_workspace_tab().click()
        # self.click_element(lc_land_page.get_workspace_tab())
        logger.info("Capture the screenshot")
        capture_screenshot(request)
