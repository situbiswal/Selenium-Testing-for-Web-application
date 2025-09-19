import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from startup import BaseTest

class LoginTest(BaseTest):
    def test_login(self):
        wait = WebDriverWait(self.driver, 20)
        try:
            print("Test case started successfully.<br>")
            llogin_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "LoginButton")))
            llogin_button.click()

            print("Click on Username and password toggle button.<br>")
            username_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter username']")))
            username_field.clear()
            username_field.send_keys("Eru")

            print("Enter Password.<br>")
            password_field = wait.until(EC.element_to_be_clickable((By.ID, "userpassword")))
            password_field.clear()
            password_field.send_keys("M1t1g@t0r")

            print("Click on Login button.<br>")
            login_button = wait.until(EC.element_to_be_clickable((By.ID, "loginBtn")))
            login_button.click()
            print("Test case end.<br>")

            wait.until(EC.url_contains("Index"))
            welcome_message = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//label[@class='form-control' and contains(text(),'iRISWebTemplate')]")
                )
            ).text
            self.assertIn("iRISWebTemplate", welcome_message)

        except Exception as e:
            print("Exception during test:", type(e).__name__, e)
            traceback.print_exc()
            raise
