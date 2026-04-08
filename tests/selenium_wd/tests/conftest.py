"""
Спільні pytest-фікстури для Selenium WebDriver тестів.
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope='session')
def driver():
    """
    Ініціалізує Chrome WebDriver один раз на сесію.
    webdriver-manager автоматично завантажує правильну версію ChromeDriver.
    """
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-notifications')
    options.add_argument('--start-maximized')
    # Розкоментуйте для headless-режиму (CI/CD):
    # options.add_argument('--headless=new')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)

    yield driver

    driver.quit()


@pytest.fixture(autouse=True)
def clean_session(driver):
    """Очищає cookies перед кожним тестом — незалежність тестів."""
    driver.delete_all_cookies()
    driver.get('http://localhost:5000/')
    yield
