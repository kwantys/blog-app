"""
Step definitions для profile.feature
"""
import sys
import os
import pytest
from pytest_bdd import given, when, then, parsers, scenarios
from selenium.webdriver.common.by import By

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'selenium_wd'))
from pages import LoginPage, ProfilePage

BASE_URL = 'http://localhost:5000'

scenarios('../features/profile.feature')


# ── Given ──────────────────────────────────────────────────────────

@given('браузер відкрито і додаток доступний')
def browser_open(driver):
    driver.get(BASE_URL)


@given('я не авторизований')
def not_authenticated(driver):
    driver.delete_all_cookies()
    driver.get(BASE_URL)


@given(parsers.parse('я увійшов як "{username}" з паролем "{password}"'))
def logged_in(driver, username, password):
    LoginPage(driver).login(username, password)


# ── When ───────────────────────────────────────────────────────────

@when('я переходжу на сторінку профілю')
def go_to_profile(driver):
    ProfilePage(driver).open()


@when('я намагаюсь перейти на сторінку профілю')
def try_open_profile(driver):
    driver.get(BASE_URL + '/users/settings/profile')


@when(parsers.parse("я вводжу ім'я \"{firstname}\""))
def enter_firstname(driver, firstname):
    ProfilePage(driver).enter_firstname(firstname)


@when(parsers.parse('я вводжу прізвище "{lastname}"'))
def enter_lastname(driver, lastname):
    ProfilePage(driver).enter_lastname(lastname)


@when(parsers.parse('я вводжу біо "{bio}"'))
def enter_bio(driver, bio):
    ProfilePage(driver).enter_bio(bio)


@when('я зберігаю профіль')
def save_profile(driver):
    ProfilePage(driver).save()


@when(parsers.parse('я відкриваю публічний профіль користувача "{username}"'))
def open_public_profile(driver, username):
    driver.get(f'{BASE_URL}/users/{username}')


# ── Then ───────────────────────────────────────────────────────────

@then('я бачу повідомлення про успіх')
def see_success(driver):
    page = ProfilePage(driver)
    assert page.has_success_alert()


@then(parsers.parse('сторінка містить текст "{text}"'))
def page_has_text(driver, text):
    assert text in driver.page_source


@then(parsers.parse('URL містить "{fragment}"'))
def url_contains(driver, fragment):
    assert fragment in driver.current_url


@then('поле імені присутнє на сторінці')
def firstname_visible(driver):
    page = ProfilePage(driver)
    assert page.is_visible(*ProfilePage.FIRSTNAME_INPUT)


@then('поле прізвища присутнє на сторінці')
def lastname_visible(driver):
    page = ProfilePage(driver)
    assert page.is_visible(*ProfilePage.LASTNAME_INPUT)


@then('поле біо присутнє на сторінці')
def bio_visible(driver):
    page = ProfilePage(driver)
    assert page.is_visible(*ProfilePage.BIO_INPUT)
