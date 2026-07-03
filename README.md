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
git clone https://github.com/ZLLLMY/web_auto.git
cd web_auto
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

## 🛒 淘宝测试（默认 QA 环境）

| Command | Description |
|---------|-------------|
| `python Runner.py` | 运行所有测试用例 |
| `python Runner.py -m taobao` | 只运行淘宝相关测试（登录、搜索、完整流程） |
| `python Runner.py -m smoke` | 只运行冒烟测试（快速验证核心功能） |
| `python Runner.py -k taobao_login` | 只运行淘宝登录测试 |
| `python Runner.py -k taobao_search` | 只运行淘宝搜索测试 |
| `python Runner.py -k taobao_full_flow` | 只运行淘宝完整流程（登录→搜索→加购） |
| `python Runner.py --env=QA` | 加载 QA 环境配置（淘宝线上环境） |
| `python Runner.py --env=dev` | 加载 dev 环境配置（开发/练习环境） |
| `python Runner.py --browser_name=chrome` | 使用 Chrome 浏览器运行 |
| `python Runner.py --browser_name=firefox` | 使用 Firefox 浏览器运行 |
| `python Runner.py -r "3"` | 所有测试重复运行 3 次 |
| `python Runner.py -m taobao -r "2"` | 淘宝测试重复运行 2 次 |

## 🔧 组合示例

```bash
# 淘宝完整流程 + QA 环境 + Chrome 浏览器 + 重复2次
python Runner.py -k taobao_full_flow --env=QA --browser_name=chrome -r "2"

# 所有淘宝标记用例 + Firefox 浏览器
python Runner.py -m taobao --browser_name=firefox

# 冒烟测试 + dev 环境
python Runner.py -m smoke --env=dev
```

---

# 👤 Author
**张龙龙**  
📍 中国  
💼 测试工程师 | 测试开发工程师 | Python
