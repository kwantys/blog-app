"""
Step definitions для auth.feature
"""
import sys
import os
import pytest
from pytest_bdd import given, when, then, parsers, scenarios

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'selenium_wd'))
from pages import LoginPage, RegisterPage, ForgotPasswordPage, MainPage

BASE_URL = 'http://localhost:5000'

scenarios('../features/auth.feature')


# ── Given ──────────────────────────────────────────────────────────

@given('браузер відкрито і додаток доступний')
def browser_open(driver):
    driver.get(BASE_URL)


@given('я перейшов на сторінку реєстрації')
def open_register(driver):
    RegisterPage(driver).open()


@given('я перейшов на сторінку входу')
def open_login(driver):
    LoginPage(driver).open()


@given('я перейшов на сторінку забули пароль')
def open_forgot(driver):
    ForgotPasswordPage(driver).open()


@given('я не авторизований')
def not_authenticated(driver):
    driver.delete_all_cookies()
    driver.get(BASE_URL)


@given(parsers.parse('я увійшов як "{username}" з паролем "{password}"'))
def logged_in(driver, username, password):
    LoginPage(driver).login(username, password)


# ── When ───────────────────────────────────────────────────────────

@when(parsers.parse('я вводжу username "{username}"'))
def enter_username_reg(driver, username):
    RegisterPage(driver).enter_username(username)


@when(parsers.parse('я вводжу email "{email}"'))
def enter_email_reg(driver, email):
    RegisterPage(driver).enter_email(email)


@when(parsers.parse('я вводжу пароль "{password}"'))
def enter_password_reg(driver, password):
    RegisterPage(driver).enter_password(password)


@when(parsers.parse('я підтверджую пароль "{password}"'))
def enter_confirm_reg(driver, password):
    RegisterPage(driver).enter_confirm(password)


@when('я натискаю кнопку реєстрації')
def click_register(driver):
    RegisterPage(driver).submit()


@when(parsers.parse('я вводжу username для входу "{username}"'))
def enter_username_login(driver, username):
    LoginPage(driver).enter_username(username)


@when(parsers.parse('я вводжу пароль для входу "{password}"'))
def enter_password_login(driver, password):
    LoginPage(driver).enter_password(password)


@when('я натискаю кнопку входу')
def click_login(driver):
    LoginPage(driver).submit()


@when('я натискаю кнопку виходу')
def click_logout(driver):
    page = LoginPage(driver)
    page.logout()


@when(parsers.parse('я вводжу email для скидання "{email}"'))
def enter_forgot_email(driver, email):
    ForgotPasswordPage(driver).enter_email(email)


@when('я натискаю кнопку відправки')
def click_forgot_submit(driver):
    ForgotPasswordPage(driver).submit()


@when('я намагаюсь перейти на сторінку створення поста')
def try_open_create_post(driver):
    driver.get(BASE_URL + '/post')


# ── Then ───────────────────────────────────────────────────────────

@then('я бачу повідомлення про успіх')
def see_success_alert(driver):
    page = LoginPage(driver)
    assert page.has_success_alert(), 'Очікувалось повідомлення про успіх'


@then('я бачу повідомлення про помилку')
def see_error_alert(driver):
    page = LoginPage(driver)
    assert page.has_error_alert(), 'Очікувалось повідомлення про помилку'


@then(parsers.parse('сторінка містить текст "{text}"'))
def page_contains_text(driver, text):
    assert text in driver.page_source, f'Текст "{text}" не знайдено на сторінці'


@then('я знаходжусь на головній сторінці')
def on_main_page(driver):
    assert driver.current_url == BASE_URL + '/'


@then('я знаходжусь на сторінці входу')
def on_login_page(driver):
    assert driver.current_url == BASE_URL + '/auth/login'


@then('я залишаюсь на сторінці реєстрації')
def stay_on_register(driver):
    assert driver.current_url == BASE_URL + '/auth/register'


@then('кнопка виходу присутня в navbar')
def logout_btn_visible(driver):
    page = LoginPage(driver)
    assert page.is_logged_in(), 'Кнопка logout має бути присутня'


@then('кнопка виходу відсутня в navbar')
def logout_btn_absent(driver):
    page = LoginPage(driver)
    assert not page.is_logged_in(), 'Кнопка logout має бути відсутня'


@then('поле email присутнє на сторінці')
def email_field_visible(driver):
    from selenium.webdriver.common.by import By
    page = ForgotPasswordPage(driver)
    assert page.is_visible(By.ID, 'email')


@then(parsers.parse('URL містить "{fragment}"'))
def url_contains(driver, fragment):
    assert fragment in driver.current_url, \
        f'Очікувався fragment "{fragment}" в URL "{driver.current_url}"'


@then('на сторінці є alert повідомлення')
def alert_present(driver):
    from selenium.webdriver.common.by import By
    page = ForgotPasswordPage(driver)
    assert page.is_visible(By.CSS_SELECTOR, '.alert')
