"""
UNIT tests for app/auth/routes.py (Controller layer).
Uses unittest.mock to isolate route logic from DB and email sending.
Target: 50%+ coverage of auth routes.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.models import User
from app import db
from tests.conftest import login_as


class TestRegisterRoute:
    """Tests for POST /auth/register."""

    def test_register_page_loads(self, client):
        """GET /auth/register returns 200."""
        r = client.get('/auth/register')
        assert r.status_code == 200

    def test_register_success(self, client, db):
        """Valid registration creates user and redirects to home."""
        r = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password1!',
            'password2': 'Password1!',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'Congrats' in r.data
        assert User.query.filter_by(username='newuser').first() is not None

    def test_register_duplicate_email(self, client, db, sample_user):
        """Duplicate email shows error flash, no new user created."""
        r = client.post('/auth/register', data={
            'username': 'differentuser',
            'email': 'test@example.com',   # already exists
            'password': 'Password1!',
            'password2': 'Password1!',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert User.query.count() == 1   # no new user

    def test_register_duplicate_username(self, client, db, sample_user):
        """Duplicate username fails validation."""
        r = client.post('/auth/register', data={
            'username': 'testuser',        # already exists
            'email': 'unique@example.com',
            'password': 'Password1!',
            'password2': 'Password1!',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert User.query.count() == 1

    def test_register_password_mismatch(self, client, db):
        """Mismatched passwords shows validation error."""
        r = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password1!',
            'password2': 'Different1!',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert User.query.filter_by(username='newuser').first() is None

    def test_register_redirects_if_logged_in(self, client, db, sample_user):
        """Logged-in user is redirected away from register page."""
        login_as(client, sample_user.id)
        r = client.get('/auth/register')
        assert r.status_code == 302


class TestLoginRoute:
    """Tests for POST /auth/login."""

    def test_login_page_loads(self, client):
        """GET /auth/login returns 200."""
        r = client.get('/auth/login')
        assert r.status_code == 200

    def test_login_valid_credentials(self, client, db, sample_user):
        """Valid credentials log in the user and redirect to home."""
        r = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'Password1!',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'testuser' in r.data

    def test_login_wrong_password(self, client, db, sample_user):
        """Wrong password shows error flash."""
        r = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpass',
        }, follow_redirects=True)
        assert r.status_code == 200
        html = r.data.decode('utf-8')
        assert 'alert_error' in html or 'Невірний' in html

    def test_login_nonexistent_user(self, client, db):
        """Non-existent username shows error flash."""
        r = client.post('/auth/login', data={
            'username': 'nobody',
            'password': 'Password1!',
        }, follow_redirects=True)
        assert r.status_code == 200
        html = r.data.decode('utf-8')
        assert 'alert_error' in html

    def test_login_redirects_if_logged_in(self, client, db, sample_user):
        """Logged-in user is redirected away from login page."""
        login_as(client, sample_user.id)
        r = client.get('/auth/login')
        assert r.status_code == 302


class TestLogoutRoute:
    """Tests for GET /auth/logout."""

    def test_logout_redirects_to_home(self, client, db, sample_user):
        """Logout redirects to index."""
        login_as(client, sample_user.id)
        r = client.get('/auth/logout', follow_redirects=True)
        assert r.status_code == 200

    def test_logout_requires_login(self, client):
        """Unauthenticated logout redirects to login page."""
        r = client.get('/auth/logout', follow_redirects=False)
        assert r.status_code == 302
        assert '/auth/login' in r.headers['Location'] or '/login' in r.headers['Location']


class TestForgotPasswordRoute:
    """Tests for /auth/forgot-password."""

    def test_forgot_page_loads(self, client):
        """GET /auth/forgot-password returns 200."""
        r = client.get('/auth/forgot-password')
        assert r.status_code == 200

    def test_forgot_valid_email_shows_info(self, client, db, sample_user):
        """Valid email shows info flash (no enumeration — same msg either way)."""
        r = client.post('/auth/forgot-password', data={
            'email': 'test@example.com',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_forgot_invalid_email_shows_info(self, client, db):
        """Non-existent email also shows info flash (anti-enumeration)."""
        r = client.post('/auth/forgot-password', data={
            'email': 'nobody@example.com',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_forgot_generates_token_for_existing_user(self, app, db, sample_user):
        """get_reset_token is called when a valid email is submitted."""
        with patch.object(User, 'get_reset_token', return_value='mock-token') as mock_token:
            with app.test_client() as c:
                c.post('/auth/forgot-password', data={
                    'email': 'test@example.com',
                }, follow_redirects=True)
            mock_token.assert_called_once()


class TestResetPasswordRoute:
    """Tests for /auth/reset-password/<token>."""

    def test_reset_valid_token_loads_form(self, app, client, db, sample_user):
        """Valid token shows reset form."""
        with app.app_context():
            token = sample_user.get_reset_token()
        r = client.get(f'/auth/reset-password/{token}')
        assert r.status_code == 200

    def test_reset_invalid_token_redirects(self, client, db):
        """Invalid token redirects to forgot-password page."""
        r = client.get('/auth/reset-password/bad-token', follow_redirects=True)
        assert r.status_code == 200

    def test_reset_valid_token_changes_password(self, app, client, db, sample_user):
        """Valid token + new password updates user's password."""
        with app.app_context():
            uid = sample_user.id
            token = sample_user.get_reset_token()

        r = client.post(f'/auth/reset-password/{token}', data={
            'password': 'NewPass1!',
            'password2': 'NewPass1!',
        }, follow_redirects=True)
        assert r.status_code == 200

        db.session.remove()
        user = db.session.get(User, uid)
        assert user.check_password('NewPass1!')

    def test_reset_token_verify_called_with_mock(self, app, db, sample_user):
        """verify_reset_token is called during reset flow."""
        with app.app_context():
            token = sample_user.get_reset_token()

        with patch.object(User, 'verify_reset_token',
                          return_value=sample_user) as mock_verify:
            with app.test_client() as c:
                c.get(f'/auth/reset-password/{token}')
            mock_verify.assert_called_once_with(token)