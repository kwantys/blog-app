"""
UNIT tests for app/users/routes.py (Controller layer).
Covers: profile view, edit profile, change password.
Target: 50%+ coverage of users routes.
"""
import pytest
from app.models import User
from app import db
from tests.conftest import login_as


class TestProfileRoute:
    """Tests for GET /users/<username>."""

    def test_profile_loads(self, client, db, sample_user):
        """Existing user's profile page returns 200."""
        r = client.get(f'/users/{sample_user.username}')
        assert r.status_code == 200

    def test_profile_shows_username(self, client, db, sample_user):
        """Profile page displays username."""
        r = client.get(f'/users/{sample_user.username}')
        assert b'testuser' in r.data

    def test_profile_404_for_missing_user(self, client, db):
        """Non-existent user returns 404."""
        r = client.get('/users/nobody')
        assert r.status_code == 404

    def test_profile_shows_posts(self, client, db, sample_user, sample_post):
        """Profile page shows user's posts."""
        r = client.get(f'/users/{sample_user.username}')
        assert b'Test Post' in r.data


class TestMyProfileAlias:
    """Tests for GET /users/profile alias."""

    def test_profile_alias_requires_login(self, client):
        """Unauthenticated /users/profile redirects to login."""
        r = client.get('/users/profile')
        assert r.status_code == 302

    def test_profile_alias_redirects_to_edit(self, client, db, sample_user):
        """Logged-in user gets redirected to edit_profile."""
        login_as(client, sample_user.id)
        r = client.get('/users/profile', follow_redirects=False)
        assert r.status_code == 302


class TestEditProfileRoute:
    """Tests for GET/POST /users/settings/profile."""

    def test_edit_profile_requires_login(self, client):
        """Unauthenticated access redirects to login."""
        r = client.get('/users/settings/profile')
        assert r.status_code == 302

    def test_edit_profile_page_loads(self, client, db, sample_user):
        """Authenticated user can access edit profile page."""
        login_as(client, sample_user.id)
        r = client.get('/users/settings/profile')
        assert r.status_code == 200

    def test_edit_profile_success(self, client, db, sample_user):
        """Valid data updates profile and shows success flash."""
        login_as(client, sample_user.id)
        r = client.post('/users/settings/profile', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'bio': 'New bio text',
            'firstname': 'Updated',
            'lastname': 'Name',
            'age': '30',
            'gender': 'M',
            'address': 'New Street',
            'website': 'https://example.com',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'Profile updated successfully!' in r.data

    def test_edit_profile_updates_bio(self, client, db, sample_user):
        """Bio is actually updated in DB."""
        login_as(client, sample_user.id)
        client.post('/users/settings/profile', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'bio': 'My updated bio',
            'firstname': '', 'lastname': '',
            'age': '', 'gender': '', 'address': '', 'website': '',
        }, follow_redirects=True)
        db.session.expire_all()
        user = db.session.get(User, sample_user.id)
        assert user.bio == 'My updated bio'

    def test_edit_profile_updates_extended_fields(self, client, db, sample_user):
        """Extended fields (firstname, age, gender) are updated."""
        login_as(client, sample_user.id)
        client.post('/users/settings/profile', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'bio': '',
            'firstname': 'Olena',
            'lastname': 'Petrenko',
            'age': '28',
            'gender': 'F',
            'address': 'Kyiv',
            'website': '',
        }, follow_redirects=True)
        db.session.expire_all()
        user = db.session.get(User, sample_user.id)
        assert user.firstname == 'Olena'
        assert user.age == '28'
        assert user.gender == 'F'

    def test_edit_profile_duplicate_email_rejected(self, client, db, sample_user, second_user):
        """Cannot change email to one already taken by another user."""
        login_as(client, sample_user.id)
        r = client.post('/users/settings/profile', data={
            'username': 'testuser',
            'email': 'other@example.com',   # belongs to second_user
            'bio': '', 'firstname': '', 'lastname': '',
            'age': '', 'gender': '', 'address': '', 'website': '',
        }, follow_redirects=True)
        assert r.status_code == 200
        db.session.expire_all()
        user = db.session.get(User, sample_user.id)
        assert user.email == 'test@example.com'   # unchanged


class TestChangePasswordRoute:
    """Tests for GET/POST /users/settings/password."""

    def test_change_password_requires_login(self, client):
        """Unauthenticated access redirects."""
        r = client.get('/users/settings/password')
        assert r.status_code == 302

    def test_change_password_page_loads(self, client, db, sample_user):
        """Page loads for authenticated user."""
        login_as(client, sample_user.id)
        r = client.get('/users/settings/password')
        assert r.status_code == 200

    def test_change_password_success(self, client, db, sample_user):
        """Valid current password allows change."""
        login_as(client, sample_user.id)
        r = client.post('/users/settings/password', data={
            'current_password': 'Password1!',
            'new_password': 'NewPass2!',
            'new_password2': 'NewPass2!',
        }, follow_redirects=True)
        assert r.status_code == 200
        db.session.expire_all()
        user = db.session.get(User, sample_user.id)
        assert user.check_password('NewPass2!')

    def test_change_password_wrong_current(self, client, db, sample_user):
        """Wrong current password shows error, password NOT changed."""
        login_as(client, sample_user.id)
        r = client.post('/users/settings/password', data={
            'current_password': 'WrongPassword!',
            'new_password': 'NewPass2!',
            'new_password2': 'NewPass2!',
        }, follow_redirects=True)
        assert r.status_code == 200
        db.session.expire_all()
        user = db.session.get(User, sample_user.id)
        assert user.check_password('Password1!')   # unchanged

    def test_change_password_mismatch(self, client, db, sample_user):
        """Mismatched new passwords fail validation."""
        login_as(client, sample_user.id)
        r = client.post('/users/settings/password', data={
            'current_password': 'Password1!',
            'new_password': 'NewPass2!',
            'new_password2': 'Different3!',
        }, follow_redirects=True)
        assert r.status_code == 200
        db.session.expire_all()
        user = db.session.get(User, sample_user.id)
        assert user.check_password('Password1!')   # unchanged