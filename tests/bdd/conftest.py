"""
Спільні фікстури для BDD тестів (pytest-bdd + Selenium).
"""
import sys
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Додаємо шлях до Page Object з лаб 8
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'selenium_wd'))


@pytest.fixture(scope='session')
def driver():
    """Chrome WebDriver — один на всю сесію."""
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-notifications')
    options.add_argument('--start-maximized')
    # Розкоментуйте для CI/CD (headless):
    # options.add_argument('--headless=new')

    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


@pytest.fixture(autouse=True)
def clean_session(driver):
    """Очищає cookies перед кожним сценарієм."""
    driver.delete_all_cookies()
    driver.get('http://localhost:5000/')
    yield
