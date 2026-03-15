"""
UNIT tests for app/models.py
Covers: User, Post, Comment — 100% of model logic.
"""
import pytest
from datetime import datetime, timezone
from app.models import User, Post, Comment
from app import db


class TestUserModel:
    """Tests for the User model."""

    def test_user_creation(self, db, sample_user):
        """User is saved to DB with correct fields."""
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'
        assert user.firstname == 'Test'
        assert user.lastname == 'User'
        assert user.age == '25'
        assert user.gender == 'M'

    def test_user_repr(self, db, sample_user):
        """__repr__ returns expected string."""
        assert repr(sample_user) == '<User testuser>'

    def test_password_hashing(self, db, sample_user):
        """Password is hashed — plain text is NOT stored."""
        assert sample_user.password_hash != 'Password1!'
        assert sample_user.password_hash is not None

    def test_check_password_correct(self, db, sample_user):
        """check_password returns True for correct password."""
        assert sample_user.check_password('Password1!') is True

    def test_check_password_wrong(self, db, sample_user):
        """check_password returns False for wrong password."""
        assert sample_user.check_password('wrongpassword') is False

    def test_check_password_empty(self, db, sample_user):
        """check_password returns False for empty string."""
        assert sample_user.check_password('') is False

    def test_set_password_updates_hash(self, db, sample_user):
        """set_password changes the password hash."""
        old_hash = sample_user.password_hash
        sample_user.set_password('NewPassword2!')
        db.session.commit()
        assert sample_user.password_hash != old_hash
        assert sample_user.check_password('NewPassword2!') is True
        assert sample_user.check_password('Password1!') is False

    def test_get_reset_token(self, app, db, sample_user):
        """get_reset_token returns a non-empty string token."""
        with app.app_context():
            token = sample_user.get_reset_token()
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 10

    def test_verify_reset_token_valid(self, app, db, sample_user):
        """verify_reset_token returns user for a valid token."""
        with app.app_context():
            token = sample_user.get_reset_token()
            user = User.verify_reset_token(token)
            assert user is not None
            assert user.id == sample_user.id

    def test_verify_reset_token_invalid(self, app, db):
        """verify_reset_token returns None for a bad token."""
        with app.app_context():
            result = User.verify_reset_token('invalid-token-xyz')
            assert result is None

    def test_verify_reset_token_expired(self, app, db, sample_user):
        """verify_reset_token returns None for an expired token (max_age=0)."""
        with app.app_context():
            token = sample_user.get_reset_token()
            result = User.verify_reset_token(token, max_age=-1)
            assert result is None

    def test_posts_count_zero(self, db, sample_user):
        """posts_count is 0 for new user."""
        assert sample_user.posts_count == 0

    def test_posts_count_after_adding(self, db, sample_user):
        """posts_count reflects actual number of posts."""
        post1 = Post(title='P1', description='d', body='b', author=sample_user)
        post2 = Post(title='P2', description='d', body='b', author=sample_user)
        db.session.add_all([post1, post2])
        db.session.commit()
        assert sample_user.posts_count == 2

    def test_comments_count_zero(self, db, sample_user):
        """comments_count is 0 for new user."""
        assert sample_user.comments_count == 0

    def test_comments_count_after_adding(self, db, sample_user, sample_post):
        """comments_count reflects actual number of comments."""
        c = Comment(name='T', content='hi', author=sample_user, post=sample_post)
        db.session.add(c)
        db.session.commit()
        assert sample_user.comments_count == 1

    def test_username_unique_constraint(self, db, sample_user):
        """Creating a second user with the same username raises an error."""
        from sqlalchemy.exc import IntegrityError
        dup = User(username='testuser', email='other2@example.com')
        dup.set_password('pass')
        db.session.add(dup)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_email_unique_constraint(self, db, sample_user):
        """Creating a second user with the same email raises an error."""
        from sqlalchemy.exc import IntegrityError
        dup = User(username='uniqueuser', email='test@example.com')
        dup.set_password('pass')
        db.session.add(dup)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_created_at_set_automatically(self, db, sample_user):
        """created_at is set automatically on creation."""
        assert sample_user.created_at is not None
        assert isinstance(sample_user.created_at, datetime)

    def test_user_is_active_by_default(self, db, sample_user):
        """Flask-Login: is_active returns True by default."""
        assert sample_user.is_active is True

    def test_user_is_authenticated(self, db, sample_user):
        """Flask-Login: is_authenticated returns True for persisted user."""
        assert sample_user.is_authenticated is True

    def test_get_id(self, db, sample_user):
        """Flask-Login: get_id returns string representation of user id."""
        assert sample_user.get_id() == str(sample_user.id)


class TestPostModel:
    """Tests for the Post model."""

    def test_post_creation(self, db, sample_post):
        """Post is saved to DB with correct fields."""
        post = Post.query.filter_by(title='Test Post').first()
        assert post is not None
        assert post.description == 'Short desc'
        assert post.body == 'Long body content.'

    def test_post_repr(self, db, sample_post):
        """__repr__ returns expected string."""
        assert repr(sample_post) == "<Post 'Test Post'>"

    def test_post_author_relationship(self, db, sample_post, sample_user):
        """Post.author returns the correct User object."""
        assert sample_post.author.id == sample_user.id
        assert sample_post.author.username == 'testuser'

    def test_post_comments_count_zero(self, db, sample_post):
        """New post has 0 comments."""
        assert sample_post.comments_count == 0

    def test_post_comments_count_after_adding(self, db, sample_post, sample_user):
        """comments_count increases when comments are added."""
        c1 = Comment(name='A', content='c1', author=sample_user, post=sample_post)
        c2 = Comment(name='B', content='c2', author=sample_user, post=sample_post)
        db.session.add_all([c1, c2])
        db.session.commit()
        assert sample_post.comments_count == 2

    def test_post_created_at_auto(self, db, sample_post):
        """created_at is set automatically."""
        assert sample_post.created_at is not None
        assert isinstance(sample_post.created_at, datetime)

    def test_post_cascade_delete_comments(self, db, sample_post, sample_user):
        """Deleting a post also deletes its comments (cascade)."""
        c = Comment(name='T', content='hi', author=sample_user, post=sample_post)
        db.session.add(c)
        db.session.commit()
        assert Comment.query.count() == 1

        db.session.delete(sample_post)
        db.session.commit()
        assert Comment.query.count() == 0

    def test_post_requires_title(self, db, sample_user):
        """Post without title raises IntegrityError."""
        from sqlalchemy.exc import IntegrityError
        post = Post(description='d', body='b', author=sample_user)
        db.session.add(post)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_post_requires_body(self, db, sample_user):
        """Post without body raises IntegrityError."""
        from sqlalchemy.exc import IntegrityError
        post = Post(title='T', description='d', author=sample_user)
        db.session.add(post)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


class TestCommentModel:
    """Tests for the Comment model."""

    def test_comment_creation(self, db, sample_comment):
        """Comment is saved with correct fields."""
        comment = Comment.query.first()
        assert comment is not None
        assert comment.name == 'Tester'
        assert comment.content == 'Nice post!'

    def test_comment_repr(self, db, sample_comment):
        """__repr__ returns expected string."""
        assert 'Comment' in repr(sample_comment)

    def test_comment_author_relationship(self, db, sample_comment, sample_user):
        """Comment.author returns the correct User."""
        assert sample_comment.author.id == sample_user.id

    def test_comment_post_relationship(self, db, sample_comment, sample_post):
        """Comment.post returns the correct Post."""
        assert sample_comment.post.id == sample_post.id

    def test_comment_created_at_auto(self, db, sample_comment):
        """created_at is set automatically."""
        assert sample_comment.created_at is not None

    def test_comment_requires_content(self, db, sample_user, sample_post):
        """Comment without content raises IntegrityError."""
        from sqlalchemy.exc import IntegrityError
        c = Comment(name='X', author=sample_user, post=sample_post)
        db.session.add(c)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_multiple_comments_on_one_post(self, db, sample_post, sample_user):
        """Multiple comments can be added to one post."""
        for i in range(5):
            c = Comment(name=f'User{i}', content=f'Comment {i}',
                        author=sample_user, post=sample_post)
            db.session.add(c)
        db.session.commit()
        assert sample_post.comments_count == 5