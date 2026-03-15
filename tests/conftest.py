"""
Shared pytest fixtures for all tests.
"""
import pytest
from app import create_app, db as _db
from app.models import User, Post, Comment
from config import TestingConfig


@pytest.fixture(scope='session')
def app():
    """Create application for testing (session scope — one DB per session)."""
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide a clean DB for every test function."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()
        _db.create_all()


@pytest.fixture(scope='function')
def client(app, db):
    """Flask test client with clean DB."""
    return app.test_client()


@pytest.fixture
def sample_user(db):
    """A persisted test user."""
    user = User(username='testuser', email='test@example.com', bio='',
                firstname='Test', lastname='User', age='25',
                gender='M', address='Street 1', website='')
    user.set_password('Password1!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def second_user(db):
    """A second persisted test user (for authorization tests)."""
    user = User(username='otheruser', email='other@example.com', bio='',
                firstname='', lastname='', age='', gender='', address='', website='')
    user.set_password('Password1!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_post(db, sample_user):
    """A persisted test post."""
    post = Post(title='Test Post', description='Short desc',
                body='Long body content.', author=sample_user)
    db.session.add(post)
    db.session.commit()
    return post


@pytest.fixture
def sample_comment(db, sample_user, sample_post):
    """A persisted test comment."""
    comment = Comment(name='Tester', content='Nice post!',
                      author=sample_user, post=sample_post)
    db.session.add(comment)
    db.session.commit()
    return comment


def login(client, username='testuser', password='Password1!'):
    """Helper: log in via test client."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password,
    }, follow_redirects=True)


def login_as(client, user_id):
    """Helper: inject session directly (faster than form login)."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_id)
        sess['_fresh'] = True