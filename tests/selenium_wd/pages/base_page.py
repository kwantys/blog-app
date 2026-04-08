"""
BasePage — базовий клас для всіх Page Object.
Містить спільні методи навігації, очікування та скріншотів.
"""
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'screenshots')


class BasePage:
    BASE_URL = 'http://localhost:5000'

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout=10)
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    # ── Навігація ──────────────────────────────────────────────────
    def open(self, path='/'):
        self.driver.get(self.BASE_URL + path)
        return self

    def get_current_url(self):
        return self.driver.current_url

    def get_page_source(self):
        return self.driver.page_source

    # ── Очікування та взаємодія ────────────────────────────────────
    def find(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def find_clickable(self, by, value):
        return self.wait.until(EC.element_to_be_clickable((by, value)))

    def click(self, by, value):
        """Клік через JavaScript — уникає перекриття елементів navbar/alert."""
        el = self.find_clickable(by, value)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)
        return self

    def type_text(self, by, value, text):
        el = self.find(by, value)
        el.clear()
        el.send_keys(text)
        return self

    def get_text(self, by, value):
        return self.find(by, value).text

    def is_visible(self, by, value):
        try:
            el = self.wait.until(EC.visibility_of_element_located((by, value)))
            return el.is_displayed()
        except Exception:
            return False

    def is_present(self, by, value):
        try:
            self.find(by, value)
            return True
        except Exception:
            return False

    def contains_text(self, text):
        return text in self.driver.page_source

    def clear_session(self):
        """Видаляє cookies — гарантує неавторизований стан."""
        self.driver.delete_all_cookies()
        self.open('/')

    # ── Скріншоти ──────────────────────────────────────────────────
    def screenshot(self, step_name: str):
        """
        Робить скріншот після кожного кроку тесту.
        Файл зберігається у папці screenshots/ з унікальним іменем.
        """
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        safe_name = step_name.replace(' ', '_').replace('/', '_')
        filename = f"{timestamp}_{safe_name}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        self.driver.save_screenshot(filepath)
        return filepath

    # ── Спільні елементи (navbar, alerts) ─────────────────────────
    def is_logged_in(self):
        return self.is_visible(By.ID, 'log_out')

    def logout(self):
        self.click(By.ID, 'log_out')
        self.screenshot('after_logout')
        return self

    def get_success_alert_text(self):
        el = self.wait.until(EC.visibility_of_element_located((By.ID, 'alert_success')))
        return el.text

    def get_error_alert_text(self):
        el = self.wait.until(EC.visibility_of_element_located((By.ID, 'alert_error')))
        return el.text

    def has_success_alert(self):
        return self.is_visible(By.ID, 'alert_success')

    def has_error_alert(self):
        return self.is_visible(By.ID, 'alert_error')
