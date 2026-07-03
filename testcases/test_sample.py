import pytest
from base.base_class import BaseClass
from conftest import capture_screenshot
from pages.login_page import LoginPage
from pages.saucelab_loginpage import SauselabLoginPage
from testdata.test_samplescript_testdata import SampleScriptTestData
from utilities.helpers import Sauselab


class Test_SampleFunctionality(BaseClass):

    def test_samplescript(self, request, getData, load_config, logger):
        logger.info(f"Navigate to {load_config['base_url']}")
        self.driver.get(load_config["base_url"])
        logger.info("Capture the screenshot")
        capture_screenshot(request)
        logger.info('Create object for page')
        lp = LoginPage(self.driver)
        logger.info("Login")
        lp.login(getData["name"], getData["email"], getData["password"])
        assert True

    @pytest.fixture(params=SampleScriptTestData.sampleTestData)
    def getData(self, request):
        return request.param

    @pytest.mark.smoke
    def test_addition(self, logger):
        logger.info("I am from addition test")
        assert 2 + 2 == 4

    @pytest.mark.smoke
    def test_failure_case(self, logger):
        logger.info("I am from failure test")
        assert 2 + 3 == 6

    def test_sauselabdemo(self, request, load_config, logger):
        logger.info("Navigate to SauseLab Demo Website")
        self.driver.get(load_config['sauseLab_url'])
        logger.info("Create Object for Login Page locator class")
        sl_lp = SauselabLoginPage(self.driver)
        logger.info("Enter username")
        sl_lp.get_username_field().send_keys("standard_user")
        logger.info("Enter password")
        sl_lp.get_password_field().send_keys("secret_sauce")
        logger.info("Click on the Login button")
        sl_lp.get_login_button().click()
        capture_screenshot(request)

    def test_sauselab_multiple(self, request, load_config, get_sause_data, logger):
        logger.info("Navigate to SauseLab Demo Website")
        self.driver.get(load_config['sauseLab_url'])
        logger.info("Pass the username, password to login function to perform the login")
        Sauselab.login(self.driver, get_sause_data["username"], get_sause_data["password"])
        capture_screenshot(request)

    @pytest.fixture(params=SampleScriptTestData.sauselabData)
    def get_sause_data(self, request):
        return request.param