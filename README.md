# 🧪 Web Automation Framework (Selenium, Python, Pytest & Allure)

A modular, scalable, and ready-to-use **Test Automation Framework** built with **Selenium WebDriver**, **Python**, **Pytest**, and **Allure Reporting**. Designed with a robust architecture following the **Page Object Model (POM)** and best practices in automation for ease of use, reusability, and maintainability.

---

## 🚀 Tech Stack

- ✅ **Selenium WebDriver** – Browser automation
- ✅ **Python** – Core programming language
- ✅ **Pytest** – Test execution and fixtures
- ✅ **Allure** – Rich and interactive test reporting

---

## ✅ Features

- 🧱 **Page Object Model (POM)** design pattern for modular code
- 🪵 **Custom Logger** using Python's `logging` module
- 📸 **Automatic & Manual Screenshot Capture** on test failure and step-level validation
- 📊 **Allure Reporting** for each test run with step-wise breakdown
- 🌐 **Environment-Based Configuration** using YAML files (e.g., QA, DEV)
- 🔍 **Data-Driven Testing** via fixture parametrization
- 🔄 **Reusable Utility Methods** for cleaner test scripts
- 🧪 **Custom Pytest Hooks** for enhanced test control
- 📁 **Timestamped Reports & Screenshots** for each run
- 🧹 **Clean Folder Structure** for easy navigation and scalability

---

## 📁 Folder Structure

- `base/`          		→ Base class with reusable Selenium actions
- `configFiles/`   		→ YAML config files for different environments
- `logs/`          		→ Auto-generated logs with timestamps for each test run
- `pages/`         		→ Page Object classes for web elements and actions
- `reports/`       		→ Allure reports organized by date and time
- `screenshots/`   		→ Auto/manual screenshots stored by date and time
- `testcases/`     		→ Test scripts grouped by module
- `testdata/`      		→ Static or external test data
- `utilities/`     		→ Common utilities and helper functions
- `conftest.py`    		→ PyTest fixtures and hooks
- `pytest.ini`     		→ PyTest configuration settings
- `requirements.txt` 	→ All dependencies required to run the framework
- `Runner.py`      		→ Main script to trigger test execution
- `setup.bat`      		→ Setup script for Windows environments
- `README.md`      		→ Project documentation

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Web_Automation_Framework(Py-PyTest).git
cd Web_Automation_Framework(Py-PyTest)
```
### 2. Run Setup Script (Windows)
```bash
Setup.bat
```
### 3. Manual Setup (Alternative)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

# 🧪 Useful Commands

| Command                                  | Description                            |
|------------------------------------------|----------------------------------------|
| `python Runner.py`                       | Run all test cases                     |
| `python Runner.py -m smoke`              | Run only test which is marked as smoke |
| `python Runner.py --browser_name=chrome` | Run with Chrome browser                |
| `python Runner.py --env=qa`              | Load QA environment configs            |
| `python Runner.py -k <keyword>`          | Run only test which is keyword match   |
| `python Runner.py -r "4"`                | Run the test for 4 times               |

---

# 👤 Author
**Ramanan Ramasamy**  
📍 Bengaluru, India  
🔗 https://www.linkedin.com/in/ramanan-ramasamy/  
💼 QA AUTOMATION Engineer | PYTHON | FULL STACK QA ENGINEER
