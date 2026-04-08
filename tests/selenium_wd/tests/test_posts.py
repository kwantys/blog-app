"""
Тести постів та коментарів.
Використовує патерн Page Object.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pages import LoginPage, MainPage, CreatePostPage, PostDetailPage

BASE_URL    = 'http://localhost:5000'
VALID_USER  = 'selenium_wd_user'
VALID_PASS  = 'Password1!'
POST_TITLE  = 'Тест Selenium WebDriver'
POST_DESC   = 'Опис тестового поста'
POST_BODY   = 'Детальний текст поста, створеного через Selenium WebDriver з патерном Page Object.'


def login(driver):
    """Допоміжна функція для входу."""
    LoginPage(driver).login(VALID_USER, VALID_PASS)


class TestCreatePost:
    """TC-15 – TC-18: Створення постів."""

    def test_create_post_requires_login(self, driver):
        """TC-15: Неавторизований не може відкрити форму створення поста."""
        page = CreatePostPage(driver)
        page.open()

        assert '/auth/login' in driver.current_url
        assert page.contains_text('Sign In')

    def test_create_post_form_loads(self, driver):
        """TC-16: Форма створення поста відкривається для авторизованого."""
        login(driver)
        page = CreatePostPage(driver)
        page.open()

        assert page.get_heading() == 'Add a Blog/Post'
        assert page.is_visible(*CreatePostPage.TITLE_INPUT)
        assert page.is_visible(*CreatePostPage.DESCRIPTION_INPUT)
        assert page.is_visible(*CreatePostPage.BODY_INPUT)
        assert page.is_visible(*CreatePostPage.SUBMIT_BUTTON)

    def test_create_post_success(self, driver):
        """TC-17: Успішне створення нового поста."""
        login(driver)
        page = CreatePostPage(driver)
        page.create_post(POST_TITLE, POST_DESC, POST_BODY)

        assert page.has_success_alert(), 'Очікувалось повідомлення про успіх'
        assert page.contains_text('Blog Post posted successfully!')
        assert page.contains_text(POST_TITLE)

    def test_create_post_without_title_fails(self, driver):
        """TC-18: Пост без заголовку не створюється."""
        login(driver)
        page = CreatePostPage(driver)
        page.open()
        page.enter_description(POST_DESC)
        page.enter_body(POST_BODY)
        page.submit()

        assert driver.current_url == BASE_URL + '/posts/create'

    def test_posts_displayed_on_dashboard(self, driver):
        """TC-19: Пости відображаються на головній сторінці."""
        main = MainPage(driver)
        main.open()

        assert main.has_post_table()
        assert main.has_post_with_title(POST_TITLE)


class TestComments:
    """TC-20 – TC-21: Коментарі до постів."""

    def test_unauthenticated_has_no_comment_form(self, driver):
        """TC-20: Неавторизований не бачить форму коментаря."""
        # Спочатку знайти пост
        main = MainPage(driver)
        main.open()
        main.click_post_link(POST_TITLE)

        post_page = PostDetailPage(driver)
        assert not post_page.has_comment_form(), \
            'Форма коментаря не повинна бути присутня для неавторизованого'

    def test_add_comment_success(self, driver):
        """TC-21: Авторизований може додати коментар."""
        login(driver)
        main = MainPage(driver)
        main.open()
        main.click_post_link(POST_TITLE)

        post_page = PostDetailPage(driver)
        assert post_page.has_comment_form(), 'Форма коментаря має бути присутня'

        post_page.add_comment('WebDriver Tester', 'Коментар через Selenium WebDriver!')

        assert post_page.has_success_alert()
        assert post_page.contains_text('Comment added to the Post successfully!')
