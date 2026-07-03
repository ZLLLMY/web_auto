# 🚀 Web Automation Framework Guide 🚀

## Table of Contents
- 📘 [Prerequisites](#prerequisites)
- ✅ [Installation](#installation)
- 🧪 [Writing Test Scripts](#writing-test-scripts)
- ▶️ [Executing Tests](#executing-tests)
- 📁 [Reports and Logs](#reports-and-logs)

## ✅ Prerequisites
Before you begin, ensure that you have the following installed on your system:
- Python  3.8+
- pip (Python's package installer)
- Git (for version control)
- A code editor (e.g., VS Code, PyCharm)
- Google Chrome / Firefox installed
- Allure Commandline installed

💡 To check Allure installation:
```bash
allure --version
```

## ⚙️ Installation
### Step 0: Create the folder & Initialize the git
create the Folder in your Local directory
open this folder in command line and initialize the git by executing the below command
```bash
git init
```
### Step 1. Clone the Repository
```bash
git clone https://github.com/your-username/Web_Automation_Framework(Py-PyTest).git
cd Web_Automation_Framework(Py-PyTest)
```
### Step 2. Run Setup Script (Windows)
```bash
Setup.bat
```
### Step 3. Manual Setup (Alternative)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
## 🧪 3. Writing Test Scripts
- Write your test scripts inside the `testcases/` folder.
- Use PyTest naming conventions: functions must start with `test_`.
- Page actions should be defined in `pages/` as classes using the Page Object Model.
- Reusable actions can go into `utilities/` or `base/`.
- 📝 Example test file: `testcases/test_login.py`

## ▶️ 4. Running the Tests
### 📍 Basic Command:
```bash
python Runner.py  #run all the tests on defult browser "chrome"  and defult env "QA"
```
### 🧪 Run specific tests by tag:
```bash 
python Runner.py -m smoke
```
### 🌍 Specify browser and environment:
```bash 
python Runner.py --browser_name=chrome --env=qa
```
### 📈 Run with specific keyword / file name / classname / test method name:
```bash 
python Runner.py -k <keyword>
```
### 📊 Run the test in no of iteration or repeatation:
```bash 
python Runner.py -r 4
```
## 🗂️ 5. Where to Find Logs, Reports, Screenshots
| Folder         | Description                                                       |
| -------------- | ----------------------------------------------------------------- |
| `logs/`        | Stores log files with timestamps for each test run                |
| `reports/`     | Contains Allure report files – organized by date → time folders             |
| `screenshots/` | Contains captured screenshots – structured by date → time folders |

## 📄 6. Configuration Files
- `configFiles/*.yaml` – Stores environment-specific configurations
- `pytest.ini` – Stores pytest-level config like markers
- `conftest.py` – Manages fixtures and test setup/teardown