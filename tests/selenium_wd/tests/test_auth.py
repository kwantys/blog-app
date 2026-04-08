"""
Тести автентифікації: реєстрація, вхід, вихід, скидання паролю.
Використовує патерн Page Object.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pages import LoginPage, RegisterPage, ForgotPasswordPage, MainPage

BASE_URL = 'http://localhost:5000'
VALID_USER  = 'selenium_wd_user'
VALID_EMAIL = 'selenium_wd@example.com'
VALID_PASS  = 'Password1!'


class TestRegistration:
    """TC-01 – TC-05: Реєстрація користувачів."""

    def test_register_page_loads(self, driver):
        """TC-01: Сторінка реєстрації відкривається та містить форму."""
        page = RegisterPage(driver)
        page.open()

        assert page.get_heading() == 'Sign Up'
        assert page.is_visible(*RegisterPage.USERNAME_INPUT)
        assert page.is_visible(*RegisterPage.EMAIL_INPUT)
        assert page.is_visible(*RegisterPage.PASSWORD_INPUT)
        assert page.is_visible(*RegisterPage.CONFIRM_INPUT)
        assert page.is_visible(*RegisterPage.REGISTER_BUTTON)

    def test_register_success(self, driver):
        """TC-02: Успішна реєстрація нового користувача."""
        page = RegisterPage(driver)
        page.register(VALID_USER, VALID_EMAIL, VALID_PASS)

        assert page.has_success_alert(), 'Очікувалось повідомлення про успіх'
        assert page.contains_text('Congrats')
        assert driver.current_url == BASE_URL + '/'

    def test_register_duplicate_email(self, driver):
        """TC-03: Реєстрація з вже існуючим email — залишається на /register."""
        page = RegisterPage(driver)
        page.register('another_user_wd', VALID_EMAIL, VALID_PASS)

        assert driver.current_url == BASE_URL + '/auth/register'

    def test_register_duplicate_username(self, driver):
        """TC-04: Реєстрація з вже існуючим username — залишається на /register."""
        page = RegisterPage(driver)
        page.register(VALID_USER, 'unique_wd@example.com', VALID_PASS)

        assert driver.current_url == BASE_URL + '/auth/register'

    def test_register_password_mismatch(self, driver):
        """TC-05: Паролі не співпадають — форма не відправляється."""
        page = RegisterPage(driver)
        page.register('mismatch_wd', 'mismatch_wd@example.com',
                      VALID_PASS, 'DifferentPass!')

        assert driver.current_url == BASE_URL + '/auth/register'


class TestLogin:
    """TC-06 – TC-10: Вхід та вихід з системи."""

    def test_login_page_loads(self, driver):
        """TC-06: Сторінка входу відкривається та містить форму."""
        page = LoginPage(driver)
        page.open()

        assert page.get_heading() == 'Sign In'
        assert page.is_visible(*LoginPage.USERNAME_INPUT)
        assert page.is_visible(*LoginPage.PASSWORD_INPUT)
        assert page.is_visible(*LoginPage.LOGIN_BUTTON)

    def test_login_success(self, driver):
        """TC-07: Успішний вхід з валідними даними."""
        page = LoginPage(driver)
        page.login(VALID_USER, VALID_PASS)

        assert page.has_success_alert(), 'Очікувалось повідомлення про успіх'
        assert page.is_logged_in(), 'Кнопка logout має бути присутня'
        assert driver.current_url == BASE_URL + '/'

    def test_login_wrong_password(self, driver):
        """TC-08: Вхід з невірним паролем — показує помилку."""
        page = LoginPage(driver)
        page.login(VALID_USER, 'WrongPassword!')

        assert page.has_error_alert(), 'Очікувалось повідомлення про помилку'
        assert driver.current_url == BASE_URL + '/auth/login'

    def test_login_nonexistent_user(self, driver):
        """TC-09: Вхід неіснуючого користувача — показує помилку."""
        page = LoginPage(driver)
        page.login('nobody_xyz_wd', VALID_PASS)

        assert page.has_error_alert(), 'Очікувалось повідомлення про помилку'

    def test_logout_success(self, driver):
        """TC-10: Успішний вихід з системи."""
        login_page = LoginPage(driver)
        login_page.login(VALID_USER, VALID_PASS)
        assert login_page.is_logged_in()

        login_page.logout()

        assert not login_page.is_logged_in(), 'Кнопка logout має зникнути'
        assert driver.current_url == BASE_URL + '/'


class TestForgotPassword:
    """TC-11 – TC-13: Скидання паролю."""

    def test_forgot_page_loads(self, driver):
        """TC-11: Сторінка скидання паролю відкривається."""
        page = ForgotPasswordPage(driver)
        page.open()

        assert page.get_heading() == 'Forgot Password'
        assert page.is_visible(*ForgotPasswordPage.EMAIL_INPUT)
        assert page.is_visible(*ForgotPasswordPage.SUBMIT_BUTTON)

    def test_forgot_existing_email(self, driver):
        """TC-12: Запит скидання для існуючого email — редирект на login."""
        page = ForgotPasswordPage(driver)
        page.request_reset(VALID_EMAIL)

        assert '/auth/login' in driver.current_url
        assert page.is_visible(
            *(__import__('selenium.webdriver.common.by', fromlist=['By'])
              .By.CSS_SELECTOR, '.alert')
        ) or page.contains_text('посилання')

    def test_forgot_nonexistent_email(self, driver):
        """TC-13: Запит скидання для неіснуючого email — той самий результат (анти-enumeration)."""
        page = ForgotPasswordPage(driver)
        page.request_reset('nobody_wd@nowhere.com')

        assert '/auth/login' in driver.current_url

    def test_unauthenticated_cannot_access_create_post(self, driver):
        """TC-14: Неавторизований не може перейти на створення поста."""
        page = ForgotPasswordPage(driver)  # будь-яка сторінка для доступу до методів
        page.open('/post')

        assert '/auth/login' in driver.current_url
        assert page.contains_text('Sign In')
