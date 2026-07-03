import inspect
import logging
import os
from datetime import datetime
import allure
import pytest
import yaml
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

driver = None

def pytest_addoption(parser):
    parser.addoption("--browser_name", action="store", default="chrome", help="Browser Selection")
    parser.addoption("--run_folder", action="store", help="Folder where report/screenshots are stored")
    parser.addoption("--screenshot_dir", action="store", help="Folder where screenshots are stored")
    parser.addoption("--env", action="store", default="qa", help="Environment to run tests against: dev or qa")

@pytest.fixture()
def invokeBrowser(request):
    global driver
    browser_name = request.config.getoption("browser_name")
    print(f"Browser name is {browser_name}")
    if browser_name == "chrome":
        options = ChromeOptions()
        options.page_load_strategy = "none"
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(60)
    elif browser_name == "firefox":
        options = FirefoxOptions()
        options.page_load_strategy = "none"
        options.set_preference("permissions.default.image", 2)
        options.set_preference("browser.cache.disk.enable", True)
        options.set_preference("browser.cache.memory.enable", True)
        options.set_preference("browser.cache.disk.capacity", 1048576)
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(60)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    elif browser_name == "edge":
        options = EdgeOptions()
        options.page_load_strategy = "none"           # 不等待页面加载完成，立即返回
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-extensions")
        driver = webdriver.Edge(options=options)
        driver.set_page_load_timeout(60)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")
    driver.maximize_window()
    request.cls.driver = driver
    yield
    driver.close()


@pytest.fixture(scope="session")
def load_config(request):
    """Load environment-specific configuration."""
    env = request.config.getoption("--env").lower()  # Get from CLI
    config_path = os.path.join(os.getcwd(), "configfiles", f"{env}_config.yaml")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot automatically on failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver_instance = getattr(item.instance, "driver", None)
        if driver_instance:
            screenshot_folder = item.config.getoption("screenshot_dir")
            os.makedirs(screenshot_folder, exist_ok=True)

            test_method_name = item.name
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{test_method_name}_failure_{timestamp}.png"
            screenshot_path = os.path.join(screenshot_folder, filename)

            success = driver_instance.save_screenshot(screenshot_path)
            if success and os.path.exists(screenshot_path):
                with open(screenshot_path, "rb") as f:
                    allure.attach(f.read(), name=f"{test_method_name}_failure", attachment_type=allure.attachment_type.PNG)


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    env = session.config.getoption("--env")
    with open("reports/environment.properties", "w") as f:
        f.write(f"Environment={env}\n")

def capture_screenshot(request):
    """Capture screenshot manually."""
    driver_instance = getattr(request.node.instance, "driver", None)
    if driver_instance:
        screenshot_folder = request.config.getoption("screenshot_dir")
        os.makedirs(screenshot_folder, exist_ok=True)

        test_method_name = request.node.name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{test_method_name}_manual_{timestamp}.png"
        screenshot_path = os.path.join(screenshot_folder, filename)

        success = driver_instance.save_screenshot(screenshot_path)
        if success and os.path.exists(screenshot_path):
            with open(screenshot_path, "rb") as f:
                allure.attach(f.read(), name=f"{test_method_name}_Captured_screenshot", attachment_type=allure.attachment_type.PNG)


@pytest.fixture(scope="session", autouse=True)
def configure_logger():
    testCaseName = inspect.stack()[1][3]
    logger = logging.getLogger(testCaseName)
    os.makedirs("logs", exist_ok=True)
    log_file_name = f"logs/log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    logger.log_path = f"logs/{log_file_name}"
    if not logger.handlers:
        fileHandler = logging.FileHandler(log_file_name)
        formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.setLevel(logging.DEBUG)
    logging.root.logger = logger
    return logger


@pytest.fixture
def logger():
    testCaseName = inspect.stack()[1][3]
    return logging.getLogger(testCaseName)