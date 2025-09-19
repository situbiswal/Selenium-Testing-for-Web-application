<img width="1920" height="1080" alt="Screenshot 2025-09-19 224024" src="https://github.com/user-attachments/assets/675a9391-b8d7-4e3c-a0d2-4d4a14ee5706" />

🧪 Automation Test Runner (GUI + HTML Reports + Screenshots)
This project is a GUI-based Automation Test Runner built with Python, Tkinter (CustomTkinter), Selenium, and HtmlTestRunner. It provides a user-friendly interface for running Selenium-based test cases, generating HTML execution reports, and capturing screenshots on test failures/errors.

🚀 Key Features
GUI Application

Start and manage test execution via a modern Tkinter interface.

Browse and select test case folders easily.

Real-time console output with color-coded test statuses.

Summary cards showing total, passed, failed, error, and skipped test counts.

Test Execution

Executes Selenium-based unittest test cases.

Captures screenshots automatically on test failures or errors.

Generates clean HTML reports (via HtmlTestRunner).

Reporting & Debugging

Opens the latest HTML report in the browser with one click.

Console log with clear indicators for test start, pass, fail, error, skip.

Duration of each test displayed in real time.

📂 Folder Structure
automation-test-runner/ │── tests/ # Your Selenium unittest test cases │ ├── sample_test.py # Example test case │ │── reports/ # Auto-generated HTML & screenshot reports │ │── test_runner.py # Main GUI Application (this script) │ │── requirements.txt # Python dependencies │── README.md # Project documentation

▶ How to Run
Clone this repository:

git clone https://github.com/your-username/automation-test-runner.git cd automation-test-runner

Install dependencies:

pip install -r requirements.txt

Start the GUI:
python test_runner.py

From the app:
Enter the Application URL.

Select the test folder.

Click Start Test.

🖼️ Reports & Screenshots

HTML Reports generated in reports/ folder.

Screenshots saved automatically for failed/error tests.

✅ Sample Test Case
Here’s an example Selenium test case to try out in your tests/ folder:

import unittest from selenium.webdriver.common.by import By from test_runner import BaseTest # Import base setup/teardown class

class SampleUITest(BaseTest): def test_google_search(self): """Verify Google search box is present""" self.driver.get("https://www.google.com") search_box = self.driver.find_element(By.NAME, "q") self.assertTrue(search_box.is_displayed(), "Search box not visible!")

if name == "main": unittest.main()

⚙ Requirements
Python 3.8+

Selenium

HtmlTestRunner

CustomTkinter

Google Chrome + ChromeDriver

📊 Example Console Output [STARTED] test_google_search [PASSED] test_google_search
Total: 1 Passed: 1 Failures: 0 Errors: 0 Skipped: 0 Total Duration: 3.12s

git remote add origin https://github.com/situbiswal/Selenium-Testing-for-Web-application.git git branch -M main git push -u origin main
