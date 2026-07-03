import argparse
import os
import shutil
import subprocess
from datetime import datetime

import pytest


def run_pytest_with_allure(marker=None, keyword=None, repeat=1, browser_name="chrome", env="qa"):
    # Step 1: Generate dynamic folders for reports and screenshots
    base_report_dir = os.path.join(os.getcwd(), "reports")
    base_screenshot_dir = os.path.join(os.getcwd(), "screenshots")
    current_time = datetime.now()
    date_str = current_time.strftime("%Y-%m-%d")
    time_str = current_time.strftime("%I-%M-%S-%p")

    # Report folder location
    result_dir = os.path.join(base_report_dir, date_str, time_str)
    # Screenshot folder location (separate from reports)
    screenshot_dir = os.path.join(base_screenshot_dir, date_str, time_str)

    # Create directories for reports and screenshots
    os.makedirs(result_dir, exist_ok=True)
    os.makedirs(screenshot_dir, exist_ok=True)

    # Step 2: Prepare allure-results folder
    allure_results = os.path.join(base_report_dir, "allure-results")
    if os.path.exists(allure_results):
        shutil.rmtree(allure_results)
    os.makedirs(allure_results, exist_ok=True)

    # Step 2: Prepare pytest command
    print("[INFO] Running PyTest tests...")

    pytest_cmd = [
        "testcases",  # folder where your tests live
        f"--alluredir={allure_results}",
        f"--run_folder={result_dir}",
        f"--screenshot_dir={screenshot_dir}",
        "--count", str(repeat),  # repeat option
        "-v",
        "-s",
        f"--browser_name={browser_name}",
        f"--env={env}"
    ]

    if marker:
        pytest_cmd.extend(["-m", marker])
    if keyword:
        pytest_cmd.extend(["-k", keyword])

    exit_code = pytest.main(pytest_cmd)
    print("[INFO] Running PyTest tests...")
    # Step 4: Generate Allure HTML report
    print("\n🚀 Generating Allure HTML Report")

    # Add Allure to PATH manually for PyCharm (optional)
    os.environ["PATH"] += os.pathsep + r"C:\allure-2.43.0\bin"

    # Ensure JAVA_HOME is set correctly (Allure requires Java)
    java_home = r"C:\jdk-21.0.11.10-hotspot"
    if os.path.exists(java_home):
        os.environ["JAVA_HOME"] = java_home
    elif "JAVA_HOME" not in os.environ or not os.path.exists(os.environ["JAVA_HOME"]):
        print("[WARNING] JAVA_HOME is not set or invalid. Allure report generation may fail.")

    allure_exe = shutil.which("allure")
    if not allure_exe:
        raise FileNotFoundError("❌ 'allure' command not found. Add Allure to PATH.")

    os.makedirs(result_dir, exist_ok=True)

    allure_generate_cmd = [
        allure_exe, "generate",
        allure_results,
        "-o", result_dir,
        "--clean"
    ]

    try:
        subprocess.run(allure_generate_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] Allure report generation failed: {e}")

    print("\n✅ Test Execution Completed.")
    print(f"📂 Final HTML Report available at {result_dir}\\index.html")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PyTest with optional marker or keyword")
    parser.add_argument("-m", "--marker", help="Marker to run specific tests (pytest -m <marker>)", default=None)
    parser.add_argument("-k", "--keyword", help="Keyword to run specific tests (pytest -k <keyword>)", default=None)
    parser.add_argument("-r", "--repeat", type=int, default=1, help="Number of times to repeat tests (default=1)")
    parser.add_argument("--browser_name", action="store", default="chrome", help="Beowser Selection")
    parser.add_argument("--env", action="store", default="qa", help="Environment to run tests against: dev or qa")
    args = parser.parse_args()

    try:
        run_pytest_with_allure(marker=args.marker, keyword=args.keyword, repeat=args.repeat, browser_name=args.browser_name, env=args.env)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Test execution failed: {e}")