@echo off
echo 🔧 Setting up Python virtual environment for Web Automation...
python -m venv venv

if exist venv\Scripts\activate (
    call venv\Scripts\activate
    echo 📦 Installing dependencies from requirements.txt...
    pip install --upgrade pip
    pip install -r requirements.txt

    echo 🔍 Installing Allure Pytest adapter...
    pip install allure-pytest

    echo ✅ Web Automation Framework setup complete.
    echo 🔧 To activate the environment later, run: venv\Scripts\activate
) else (
    echo ❌ Failed to create virtual environment. Ensure Python is installed and added to PATH.
)

pause
