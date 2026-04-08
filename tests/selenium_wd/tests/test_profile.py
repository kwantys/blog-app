"""
Тести профілю користувача.
Використовує патерн Page Object.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pages import LoginPage, ProfilePage
from selenium.webdriver.common.by import By

BASE_URL    = 'http://localhost:5000'
VALID_USER  = 'selenium_wd_user'
VALID_PASS  = 'Password1!'


def login(driver):
    LoginPage(driver).login(VALID_USER, VALID_PASS)


class TestProfile:
    """TC-22 – TC-24: Профіль користувача."""

    def test_profile_requires_login(self, driver):
        """TC-22: Неавторизований не має доступу до редагування профілю."""
        page = ProfilePage(driver)
        page.open('/users/settings/profile')

        assert '/auth/login' in driver.current_url
        assert page.contains_text('Sign In')

    def test_profile_page_loads(self, driver):
        """TC-23: Сторінка профілю відкривається для авторизованого."""
        login(driver)
        page = ProfilePage(driver)
        page.open()

        assert page.get_heading() == 'Your Profile'
        assert page.is_visible(*ProfilePage.FIRSTNAME_INPUT)
        assert page.is_visible(*ProfilePage.LASTNAME_INPUT)
        assert page.is_visible(*ProfilePage.BIO_INPUT)
        assert page.is_visible(*ProfilePage.SAVE_BUTTON)

    def test_profile_update_success(self, driver):
        """TC-24: Успішне оновлення профілю."""
        login(driver)
        page = ProfilePage(driver)
        page.update_profile('Selenium', 'WebDriver', 'Тестовий користувач Selenium WD')

        assert page.has_success_alert()
        assert page.contains_text('Profile updated successfully!')

    def test_public_profile_accessible(self, driver):
        """TC-25: Публічний профіль доступний без авторизації."""
        page = ProfilePage(driver)
        page.open(f'/users/{VALID_USER}')

        assert page.contains_text(VALID_USER)
        assert page.contains_text('Posts')
