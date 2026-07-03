# 📘 Guide: How to Create Test Scripts in the Framework

This document provides a step-by-step guide to creating automated test scripts using the Selenium-Python framework. The framework is structured with modular, reusable components for configuration, test cases, pages, and utility functions.

---

## ✅ Step 1: Configure Global Variables

All environment-specific configurations like URLs, usernames, and passwords should be stored in the `configFiles/QA_config.yaml` file.

### Example: `QA_config.yaml`
```yaml
base_url: "https://www.example.com"
username: "standard_user"
password: "secret_sauce"
```
## ✅ Step 2: Create a Test File
Create a new Python file under the testcases/ folder. The filename must start with test_.
``` bash
testcases/test_login.py
```
## ✅ Step 2.1: Create a Test Class
Inside the test file, create a class with a meaningful name for the test functionality. Inherit from BaseClass to access browser initialization and reusable Selenium methods.
```bash
# testcases/test_login.py

class Test_Login_Functionality(BaseClass):
```
## ✅ Step 2.2: Define Test Methods
- Within the class, define your test methods. Prefix them with test_ to ensure pytest discovers them. 
### Use the following arguments in your test methods:
- `request`: for capturing screenshots (optional)
- `load_config`: to access environment variables from the YAML file
- `logger`: to log actions for traceability
```bash 
def test_valid_login_check(self, request, load_config, logger):
```
## ✅ Step 2.3: Logging and Screenshot Capture
Use the `logger` object to log steps and `load_config` to access test data.

### Logging Example:
```bash 
logger.info(f"Navigate to {load_config['base_url']}")
# below is the code for navigation to desired website
self.driver.get(load_config["base_url"])
```
### Screenshot Example:
```bash 
logger.info("Capture the screenshot")
#below is the reusable function to capture the screenshot
capture_screenshot(request)
```
## 🧪 Step 2:-  Final ouput 
### Example: `testcases/test_login.py`
```bash
class Test_Login_Functionality(BaseClass):

    def test_valid_login_check(self, request, load_config, logger):
        logger.info(f"Navigate to {load_config['base_url']}")
        self.driver.get(load_config["base_url"])
        logger.info("Capture the screenshot")
        capture_screenshot(request)
```
## ✅ Step 3: Create Page Object File
For each page in your application, create a corresponding Python file in the `Pages/` directory.
```bash 
Pages/login_page.py
```
## ✅ Step 3.1: Define Page Object Class
- Create a class inside the page file. 
- The class name should reflect the page name. 
- Declare the `driver: WebDriver` hint for IntelliSense support.
```bash 
class LoginPage:
    driver: WebDriver
```
## ✅ Step 3.2: Initialize the Driver
Create a constructor `(__init__)` to accept the WebDriver instance.
```bash 
def __init__(self, driver):
    self.driver = driver
```
## ✅ Step 3.3: Define Element Locators
Use private variables (`_UPPERCASE`) to define locators in tuple format.
```bash 
_USERNAME_FIELD = (By.CSS_SELECTOR, '[id="user-name"]')
```
## ✅ Step 3.4: Create Public Methods to Access Elements
Use public methods to return the WebElements using Selenium.
```bash 
def get_username_field(self):
    return self.driver.find_element(*LoginPage._USERNAME_FIELD)
```
## 🧪 Step 3:-  Final ouput 
### Example: `Pages/login_page.py`
```bash
class LoginPage:
    driver: WebDriver   #for IntelliSense support
    
    def __init__(self, driver): #Constructor to accept the WebDriver instance
        self.driver = driver
    
    #Private varibale
    _USERNAME_FIELD = (By.CSS_SELECTOR, '[id="user-name"]')
    
    #public method to return the WebElements
    def get_username_field(self):
        return self.driver.find_element(*LoginPage._USERNAME_FIELD)
```
## ✅ Step 4: Create Reusable Actions
Create a new file in the `utilities/` directory for reusable page-specific actions.
```bash 
utilities/login.py
```
## ✅ Step 4.1: Define a Utility Class
Create a class named after the page or action group.
```bash 
class LoginPage_Methods:
```
## ✅ Step 4.2: Write Reusable Static Methods
Use `@staticmethod` decorators for shared utilities such as login.
``` bash 
@staticmethod
def login(driver, username, password):
    lp = LoginPage(driver)
    lp.get_username_field().send_keys(username)
    lp.get_password_field().send_keys(password)
    lp.get_login_button().click()
```
## 🧪 Step 4:-  Final ouput 
### Example: `utilities/login.py`
```bash
class LoginPage_Methods:

    @staticmethod
    def login(driver, username, password):
        lp = LoginPage(driver)
        lp.get_username_field().send_keys(username)
        lp.get_password_field().send_keys(password)
        lp.get_login_button().click()
```
## ✅ Step 5: Use Reusable Methods in Test
In your test method, call the reusable method and pass the driver and credentials.
```bash 
logger.info("Pass the username, password to login function to perform the login")
LoginPage_Methods.login(self.driver, load_config["username"], load_config["password"])
```
## 🧪 Step 5:-  Final ouput 
### Example: `testcases/test_login.py`
```bash
class Test_Login_Functionality(BaseClass):

    def test_valid_login_check(self, request, load_config, logger):
        logger.info(f"Navigate to {load_config['base_url']}")
        self.driver.get(load_config["base_url"])
        logger.info("Capture the screenshot")
        capture_screenshot(request)
        logger.info("Pass the username, password to login function to perform the login")
        LoginPage_Methods.login(self.driver, load_config["username"], load_config["password"])
```

# 🔚 Summary
| Step      | Task Description                                            |
|-----------| ----------------------------------------------------------- |
| 1         | Store environment config in `QA_config.yaml`                |
| 2         | Create test file under `testcases/`                         |
| 2.1       | Create test class and inherit `BaseClass`                   |
| 2.2       | Define test methods with `request`, `load_config`, `logger` |
| 2.3       | Log actions and capture screenshots                         |
| 3         | Define Page Object file under `Pages/`                      |
| 3.1 - 3.4 | Implement Page Object Model with locators and accessors     |
| 4 - 4.2   | Create reusable methods under `utilities/`                  |
| 5         | Call reusable methods inside test                           |
