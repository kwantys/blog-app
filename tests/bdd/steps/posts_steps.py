"""
Step definitions для posts.feature
"""
import sys
import os
import pytest
from pytest_bdd import given, when, then, parsers, scenarios
from selenium.webdriver.common.by import By

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'selenium_wd'))
from pages import LoginPage, MainPage, CreatePostPage, PostDetailPage

BASE_URL = 'http://localhost:5000'

scenarios('../features/posts.feature')


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


@given('я перейшов на головну сторінку')
def open_main(driver):
    MainPage(driver).open()


# ── When ───────────────────────────────────────────────────────────

@when('я переходжу на сторінку створення поста')
def go_to_create_post(driver):
    CreatePostPage(driver).open()


@when(parsers.parse('я вводжу заголовок поста "{title}"'))
def enter_post_title(driver, title):
    CreatePostPage(driver).enter_title(title)


@when(parsers.parse('я вводжу опис поста "{description}"'))
def enter_post_desc(driver, description):
    CreatePostPage(driver).enter_description(description)


@when(parsers.parse('я вводжу текст поста "{body}"'))
def enter_post_body(driver, body):
    CreatePostPage(driver).enter_body(body)


@when('я натискаю кнопку публікації')
def click_publish(driver):
    CreatePostPage(driver).submit()


@when(parsers.parse('я відкриваю пост з назвою "{title}"'))
def open_post(driver, title):
    MainPage(driver).click_post_link(title)


@when(parsers.parse("я вводжу ім'я коментатора \"{name}\""))
def enter_comment_name(driver, name):
    PostDetailPage(driver).enter_comment_name(name)


@when(parsers.parse('я вводжу текст коментаря "{text}"'))
def enter_comment_text(driver, text):
    PostDetailPage(driver).enter_comment_text(text)


@when('я натискаю кнопку додавання коментаря')
def click_add_comment(driver):
    PostDetailPage(driver).submit_comment()


@when('я намагаюсь перейти на сторінку створення поста')
def try_open_create(driver):
    driver.get(BASE_URL + '/post')


# ── Then ───────────────────────────────────────────────────────────

@then('я бачу повідомлення про успіх')
def see_success(driver):
    page = MainPage(driver)
    assert page.has_success_alert()


@then(parsers.parse('сторінка містить текст "{text}"'))
def page_has_text(driver, text):
    assert text in driver.page_source


@then('я залишаюсь на сторінці створення поста')
def stay_on_create(driver):
    assert driver.current_url == BASE_URL + '/posts/create'


@then('таблиця постів присутня на сторінці')
def post_table_visible(driver):
    page = MainPage(driver)
    assert page.has_post_table()


@then('форма додавання коментаря відсутня')
def no_comment_form(driver):
    page = PostDetailPage(driver)
    assert not page.has_comment_form()


@then('поле заголовку присутнє на сторінці')
def title_field_visible(driver):
    page = CreatePostPage(driver)
    assert page.is_visible(*CreatePostPage.TITLE_INPUT)


@then('поле тексту поста присутнє на сторінці')
def body_field_visible(driver):
    page = CreatePostPage(driver)
    assert page.is_visible(*CreatePostPage.BODY_INPUT)


@then(parsers.parse('URL містить "{fragment}"'))
def url_contains(driver, fragment):
    assert fragment in driver.current_url
