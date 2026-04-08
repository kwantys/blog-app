"""
Page Object класи для всіх сторінок Blog App.
Кожен клас інкапсулює локатори та дії конкретної сторінки.
"""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


# ══════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════════
class LoginPage(BasePage):
    # Локатори
    URL = '/login'
    USERNAME_INPUT = (By.ID, 'username')
    PASSWORD_INPUT = (By.ID, 'password')
    LOGIN_BUTTON   = (By.ID, 'login')
    HEADING        = (By.CSS_SELECTOR, '.panel-heading')

    def open(self):
        super().open(self.URL)
        self.screenshot('login_page_opened')
        return self

    def enter_username(self, username: str):
        self.type_text(*self.USERNAME_INPUT, username)
        self.screenshot('login_username_entered')
        return self

    def enter_password(self, password: str):
        self.type_text(*self.PASSWORD_INPUT, password)
        self.screenshot('login_password_entered')
        return self

    def submit(self):
        self.click(*self.LOGIN_BUTTON)
        self.screenshot('login_submitted')
        return self

    def login(self, username: str, password: str):
        """Повний цикл входу в один виклик."""
        self.open()
        self.enter_username(username)
        self.enter_password(password)
        self.submit()
        return self

    def get_heading(self):
        return self.get_text(*self.HEADING)


# ══════════════════════════════════════════════════════════════════
#  REGISTER PAGE
# ══════════════════════════════════════════════════════════════════
class RegisterPage(BasePage):
    URL = '/register'
    USERNAME_INPUT  = (By.ID, 'username')
    EMAIL_INPUT     = (By.ID, 'email')
    PASSWORD_INPUT  = (By.ID, 'password')
    CONFIRM_INPUT   = (By.ID, 'confirm')
    REGISTER_BUTTON = (By.ID, 'register')
    HEADING         = (By.CSS_SELECTOR, '.panel-heading')

    def open(self):
        super().open(self.URL)
        self.screenshot('register_page_opened')
        return self

    def enter_username(self, username: str):
        self.type_text(*self.USERNAME_INPUT, username)
        self.screenshot('register_username_entered')
        return self

    def enter_email(self, email: str):
        self.type_text(*self.EMAIL_INPUT, email)
        self.screenshot('register_email_entered')
        return self

    def enter_password(self, password: str):
        self.type_text(*self.PASSWORD_INPUT, password)
        self.screenshot('register_password_entered')
        return self

    def enter_confirm(self, password: str):
        self.type_text(*self.CONFIRM_INPUT, password)
        self.screenshot('register_confirm_entered')
        return self

    def submit(self):
        self.click(*self.REGISTER_BUTTON)
        self.screenshot('register_submitted')
        return self

    def register(self, username: str, email: str, password: str, confirm: str = None):
        """Повний цикл реєстрації."""
        if confirm is None:
            confirm = password
        self.open()
        self.enter_username(username)
        self.enter_email(email)
        self.enter_password(password)
        self.enter_confirm(confirm)
        self.submit()
        return self

    def get_heading(self):
        return self.get_text(*self.HEADING)


# ══════════════════════════════════════════════════════════════════
#  FORGOT PASSWORD PAGE
# ══════════════════════════════════════════════════════════════════
class ForgotPasswordPage(BasePage):
    URL = '/forgot'
    EMAIL_INPUT    = (By.ID, 'email')
    SUBMIT_BUTTON  = (By.ID, 'forgot')
    HEADING        = (By.CSS_SELECTOR, '.panel-heading')

    def open(self):
        super().open(self.URL)
        self.screenshot('forgot_page_opened')
        return self

    def enter_email(self, email: str):
        self.type_text(*self.EMAIL_INPUT, email)
        self.screenshot('forgot_email_entered')
        return self

    def submit(self):
        self.click(*self.SUBMIT_BUTTON)
        self.screenshot('forgot_submitted')
        return self

    def request_reset(self, email: str):
        self.open()
        self.enter_email(email)
        self.submit()
        return self

    def get_heading(self):
        return self.get_text(*self.HEADING)


# ══════════════════════════════════════════════════════════════════
#  MAIN PAGE (Dashboard)
# ══════════════════════════════════════════════════════════════════
class MainPage(BasePage):
    URL = '/'
    POST_TABLE      = (By.ID, 'post_listing')
    ADD_POST_BTN    = (By.ID, 'add_new_post_btn')
    ADD_POST_LINK   = (By.ID, 'add_new_post_link')
    DASHBOARD_LINK  = (By.ID, 'dashboard')

    def open(self):
        super().open(self.URL)
        self.screenshot('main_page_opened')
        return self

    def has_post_table(self):
        return self.is_visible(*self.POST_TABLE)

    def has_post_with_title(self, title: str):
        return self.contains_text(title)

    def click_post_link(self, title: str):
        from selenium.webdriver.common.by import By
        self.click(By.LINK_TEXT, title)
        self.screenshot(f'clicked_post_{title[:20]}')
        return self

    def go_to_create_post(self):
        self.click(*self.ADD_POST_LINK)
        self.screenshot('navigated_to_create_post')
        return self


# ══════════════════════════════════════════════════════════════════
#  CREATE POST PAGE
# ══════════════════════════════════════════════════════════════════
class CreatePostPage(BasePage):
    URL = '/post'
    TITLE_INPUT       = (By.ID, 'title')
    DESCRIPTION_INPUT = (By.ID, 'description')
    BODY_INPUT        = (By.ID, 'body')
    SUBMIT_BUTTON     = (By.ID, 'post')
    HEADING           = (By.ID, 'add_post_head')

    def open(self):
        super().open(self.URL)
        self.screenshot('create_post_page_opened')
        return self

    def enter_title(self, title: str):
        self.type_text(*self.TITLE_INPUT, title)
        self.screenshot('post_title_entered')
        return self

    def enter_description(self, description: str):
        self.type_text(*self.DESCRIPTION_INPUT, description)
        self.screenshot('post_description_entered')
        return self

    def enter_body(self, body: str):
        self.type_text(*self.BODY_INPUT, body)
        self.screenshot('post_body_entered')
        return self

    def submit(self):
        self.click(*self.SUBMIT_BUTTON)
        self.screenshot('post_submitted')
        return self

    def create_post(self, title: str, description: str, body: str):
        """Повний цикл створення поста."""
        self.open()
        self.enter_title(title)
        self.enter_description(description)
        self.enter_body(body)
        self.submit()
        return self

    def get_heading(self):
        return self.get_text(*self.HEADING)


# ══════════════════════════════════════════════════════════════════
#  POST DETAIL PAGE
# ══════════════════════════════════════════════════════════════════
class PostDetailPage(BasePage):
    NAME_INPUT      = (By.ID, 'name')
    MESSAGE_INPUT   = (By.ID, 'message')
    COMMENT_BUTTON  = (By.ID, 'add_comment')

    def open(self, post_id: int):
        super().open(f'/posts/{post_id}')
        self.screenshot(f'post_detail_{post_id}_opened')
        return self

    def enter_comment_name(self, name: str):
        self.type_text(*self.NAME_INPUT, name)
        self.screenshot('comment_name_entered')
        return self

    def enter_comment_text(self, text: str):
        self.type_text(*self.MESSAGE_INPUT, text)
        self.screenshot('comment_text_entered')
        return self

    def submit_comment(self):
        self.click(*self.COMMENT_BUTTON)
        self.screenshot('comment_submitted')
        return self

    def add_comment(self, name: str, text: str):
        self.enter_comment_name(name)
        self.enter_comment_text(text)
        self.submit_comment()
        return self

    def has_comment_form(self):
        return self.is_present(*self.COMMENT_BUTTON)


# ══════════════════════════════════════════════════════════════════
#  PROFILE (EDIT) PAGE
# ══════════════════════════════════════════════════════════════════
class ProfilePage(BasePage):
    URL = '/profile'
    FIRSTNAME_INPUT = (By.ID, 'firstname')
    LASTNAME_INPUT  = (By.ID, 'lastname')
    AGE_INPUT       = (By.ID, 'age')
    BIO_INPUT       = (By.ID, 'bio')
    SAVE_BUTTON     = (By.ID, 'update_profile')
    HEADING         = (By.ID, 'profile_heading')

    def open(self):
        super().open(self.URL)
        self.screenshot('profile_page_opened')
        return self

    def enter_firstname(self, value: str):
        self.type_text(*self.FIRSTNAME_INPUT, value)
        self.screenshot('profile_firstname_entered')
        return self

    def enter_lastname(self, value: str):
        self.type_text(*self.LASTNAME_INPUT, value)
        self.screenshot('profile_lastname_entered')
        return self

    def enter_bio(self, value: str):
        self.type_text(*self.BIO_INPUT, value)
        self.screenshot('profile_bio_entered')
        return self

    def save(self):
        self.click(*self.SAVE_BUTTON)
        self.screenshot('profile_saved')
        return self

    def update_profile(self, firstname: str, lastname: str, bio: str):
        self.open()
        self.enter_firstname(firstname)
        self.enter_lastname(lastname)
        self.enter_bio(bio)
        self.save()
        return self

    def get_heading(self):
        return self.get_text(*self.HEADING)
